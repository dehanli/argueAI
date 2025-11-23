from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv

from database import init_db, get_db, Discussion, Message
from agents import MultiAgentDiscussion
from role_generator import generate_discussion_roles
from tts_handler import generate_tts, select_voice_for_role, VOICE_PROFILES, create_voice_clone

# Load environment variables
load_dotenv()

# Initialize database
init_db()

app = FastAPI(title="Multi-Agent Discussion API")

# Get project root directory
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Template configuration
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class DiscussionCreate(BaseModel):
    topic: str
    mode: str = "auto"  # Discussion mode: auto (intelligent selection) or round_robin (take turns)

class DiscussionResponse(BaseModel):
    id: int
    topic: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    agent_name: str
    content: str
    timestamp: datetime
    message_type: str

    class Config:
        from_attributes = True

# API routes
@app.get("/")
async def root(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/discussions", response_model=DiscussionResponse)
async def create_discussion(
    discussion: DiscussionCreate,
    db: Session = Depends(get_db)
):
    """Create new discussion"""
    db_discussion = Discussion(topic=discussion.topic)
    db.add(db_discussion)
    db.commit()
    db.refresh(db_discussion)
    return db_discussion

@app.get("/discussions", response_model=List[DiscussionResponse])
async def get_discussions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get discussion list"""
    discussions = db.query(Discussion).order_by(
        Discussion.created_at.desc()
    ).offset(skip).limit(limit).all()
    return discussions

@app.get("/discussions/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: int,
    db: Session = Depends(get_db)
):
    """Get single discussion"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    return discussion

@app.get("/discussions/{discussion_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    discussion_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages for discussion"""
    messages = db.query(Message).filter(
        Message.discussion_id == discussion_id
    ).order_by(Message.timestamp.asc()).all()
    return messages

# Store discussion sessions and role-voice mappings
discussion_sessions = {}

@app.post("/discussions/{discussion_id}/init")
async def init_discussion(
    discussion_id: int,
    db: Session = Depends(get_db)
):
    """Initialize discussion and generate roles"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    # Generate discussion roles
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        roles = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: generate_discussion_roles(discussion.topic, num_roles=3)
        )

    # Assign voice to each role
    role_voice_map = {}
    for role in roles:
        display_name = role.get("display_name", role["name"])
        voice_id = select_voice_for_role(display_name, role.get("personality", ""))
        role_voice_map[role["name"]] = voice_id

    # Create discussion system
    agent_system = MultiAgentDiscussion(
        message_callback=None,
        discussion_mode="auto",
        custom_roles=roles
    )
    agent_system.init_discussion(discussion.topic)

    # Save to memory
    discussion_sessions[discussion_id] = {
        "agent_system": agent_system,
        "role_voice_map": role_voice_map,
        "roles": roles
    }

    # Update discussion status
    discussion.status = "running"
    db.commit()

    return {
        "roles": [
            {
                "name": role.get("display_name", role["name"]),
                "stance": role["stance"],
                "personality": role["personality"]
            }
            for role in roles
        ]
    }

class UserMessageRequest(BaseModel):
    content: str
    voice_id: Optional[str] = None  # User selected voice ID

class ModeUpdateRequest(BaseModel):
    mode: str

@app.post("/discussions/{discussion_id}/mode")
async def update_mode(
    discussion_id: int,
    request: ModeUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update discussion mode"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    # Get session
    session = discussion_sessions.get(discussion_id)
    if not session:
        raise HTTPException(status_code=400, detail="Discussion not initialized")

    agent_system = session["agent_system"]

    # Update mode
    agent_system.discussion_mode = request.mode

    return {"status": "ok", "mode": request.mode}

@app.post("/discussions/{discussion_id}/user_message")
async def user_message(
    discussion_id: int,
    message: UserMessageRequest,
    db: Session = Depends(get_db)
):
    """Receive user message"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    # Get session
    session = discussion_sessions.get(discussion_id)
    if not session:
        raise HTTPException(status_code=400, detail="Discussion not initialized")

    agent_system = session["agent_system"]

    # Add user message to discussion history
    agent_system.add_user_message(message.content)

    # Save to database
    db_message = Message(
        discussion_id=discussion_id,
        agent_name="You",
        content=message.content,
        message_type="user"
    )
    db.add(db_message)
    db.commit()

    # Generate TTS for user message (if voice_id provided)
    audio_base64 = None
    if message.voice_id and os.getenv("FISH_AUDIO_API_KEY"):
        try:
            print(f"🎤 Generating user message TTS: ({len(message.content)}characters)")
            audio_base64 = await generate_tts(message.content, message.voice_id)
            if audio_base64:
                print(f"✅ User TTS generation completed")
        except Exception as e:
            print(f"❌ User TTS generation failed: {e}")

    return {
        "status": "ok",
        "audio": audio_base64,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/discussions/{discussion_id}/next_turn")
async def next_turn(
    discussion_id: int,
    db: Session = Depends(get_db)
):
    """Execute next turn"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    # Get session
    session = discussion_sessions.get(discussion_id)
    if not session:
        raise HTTPException(status_code=400, detail="Discussion not initialized")

    agent_system = session["agent_system"]
    role_voice_map = session["role_voice_map"]

    # Execute next_turn in thread pool
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        future = executor.submit(agent_system.next_turn)
        agent_name, content = await asyncio.get_event_loop().run_in_executor(
            None, future.result
        )

    # Discussion ended
    if agent_name is None:
        discussion.status = "completed"
        db.commit()
        del discussion_sessions[discussion_id]
        return {"status": "finished"}

    print(f"💬 [{agent_name}]: {content[:50]}...")

    # Save to database
    message = Message(
        discussion_id=discussion_id,
        agent_name=agent_name,
        content=content,
        message_type="chat"
    )
    db.add(message)
    db.commit()

    # Get voice and generate TTS
    voice_id = role_voice_map.get(agent_name, "")
    audio_base64 = None

    if voice_id and os.getenv("FISH_AUDIO_API_KEY"):
        try:
            print(f"🎤 Generating TTS: {agent_name} ({len(content)}characters)")
            audio_base64 = await generate_tts(content, voice_id)
            print(f"✅ TTS generation completed")
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")

    return {
        "status": "ongoing",
        "agent": agent_name,
        "content": content,
        "audio": audio_base64,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/voices")
async def get_voices():
    """Get available voice list"""
    # Voice name mapping
    voice_names = {
        "male_young": "Energetic Male",
        "male_mature": "Ethan",
        "female_young": "E-girl",
        "female_mature": "Sarah",
        "neutral": "Adrian"
    }

    voices = [
        {
            "id": voice_id,
            "name": voice_names.get(key, key),
            "category": key
        }
        for key, voice_id in VOICE_PROFILES.items()
    ]

    return {"voices": voices}

@app.post("/clone_voice")
async def clone_voice(
    name: str = Form(...),
    audio: UploadFile = File(...),
    description: str = Form("")
):
    """Create voice clone"""
    try:
        # Read audio file
        audio_data = await audio.read()

        # Check file size (limit 10MB)
        if len(audio_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 10MB)")

        # Check file format
        if not audio.filename.lower().endswith(('.wav', '.mp3')):
            raise HTTPException(status_code=400, detail="Only WAV and MP3 files are supported")

        # Call Fish Audio API to create voice clone
        voice_id = await create_voice_clone(name, audio_data, description)

        if not voice_id:
            raise HTTPException(status_code=500, detail="Failed to create voice clone")

        return {
            "voice_id": voice_id,
            "name": name,
            "description": description
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in clone_voice endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
