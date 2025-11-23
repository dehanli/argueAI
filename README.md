# 🤖 AI Multi-Agent Discussion System

A multi-agent discussion system based on AutoGen, allowing three AI agents—a philosopher, a scientist, and an artist—to engage in intellectual collisions from different perspectives.

## ✨ Features

- 🧙 **Three AI Agents**: Philosopher, Scientist, Artist, each expressing views from their professional perspective
- 🔍 **Real-time Search**: Agents can call DuckDuckGo Search to obtain real-world data
- 💬 **Real-time Dialogue Flow**: Push discussion progress in real-time via WebSocket
- 📚 **Discussion History**: All discussions are saved in a local SQLite database
- 🎨 **Modern UI**: React frontend with a clean chat interface

## 🏗️ Tech Stack

### Backend
- **FastAPI** - High-performance Web framework
- **AutoGen** - Multi-agent orchestration framework
- **SQLAlchemy** - ORM database management
- **WebSocket** - Real-time communication
- **DuckDuckGo Search** - Search engine API

### Frontend
- **React** - UI framework
- **Axios** - HTTP client
- **WebSocket** - Real-time message receiving

### Database
- **SQLite** - Lightweight local database

## 📦 Installation and Startup

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn
- OpenAI API Key

### 1. Clone the project (if obtaining from git)

```bash
cd multi-ai
```

### 2. Configure Environment Variables

Copy the example configuration file and fill in your OpenAI API key:

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Database Configuration
DATABASE_PATH=./backend/discussions.db
```

**⚠️ Important Security Warning**:
- **Immediately delete the hardcoded API key in test.py** (Line 70)
- Go to [OpenAI Platform](https://platform.openai.com/api-keys) to delete the leaked key
- Generate a new API key and configure it in the `.env` file
- **NEVER** commit the `.env` file to Git

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Start the Application

#### Method 1: Start Separately (Recommended for Development)

**Start Backend** (New Terminal Window):
```bash
cd backend
python main.py
```

The backend will run at `http://localhost:8000`

**Start Frontend** (New Terminal Window):
```bash
cd frontend
npm start
```

The frontend will run at `http://localhost:3000` and automatically open the browser.

#### Method 2: Use Startup Script (Optional)

Create a startup script `start.sh` (macOS/Linux):

```bash
#!/bin/bash
cd backend && python main.py &
cd frontend && npm start &
wait
```

## 🎯 Usage

1. Open browser and visit `http://localhost:3000`
2. Enter a discussion topic in the input box, for example:
   - "What is reality?"
   - "Will AI replace humans?"
   - "What should be the judging criteria for a hackathon?"
3. Click the "Start Discussion" button
4. Watch the three AI agents discuss from philosophical, scientific, and artistic perspectives
5. View discussion history on the left

## 📁 Project Structure

```
multi-ai/
├── backend/                 # Python Backend
│   ├── main.py             # FastAPI Entry
│   ├── agents.py           # AutoGen Multi-Agent Logic
│   ├── database.py         # SQLite Database Models
│   ├── requirements.txt    # Python Dependencies
│   └── discussions.db      # SQLite Database (Generated after running)
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── App.js         # Main App Component
│   │   └── App.css        # Style File
│   ├── public/
│   └── package.json       # Node.js Dependencies
├── .env                    # Environment Variables (Create manually)
├── .env.example           # Environment Variables Example
├── .gitignore             # Git Ignore File
├── test.py                # Original Command Line Version (Deprecated)
└── README.md              # This File
```

## 🔧 API Endpoints

### REST API

- `GET /` - Health Check
- `POST /discussions` - Create New Discussion
- `GET /discussions` - Get Discussion List
- `GET /discussions/{id}` - Get Single Discussion
- `GET /discussions/{id}/messages` - Get Discussion Messages

### WebSocket

- `WS /ws/discuss/{discussion_id}` - Real-time Discussion Communication

## 🐛 Common Issues

### Backend Fails to Start

**Issue**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Cannot Connect to Backend

**Issue**: Frontend shows "Connection error, please check if backend is running"

**Solution**:
1. Confirm backend is started: Visit `http://localhost:8000`
2. Check CORS configuration (Already configured in code)
3. Check if port is occupied

### OpenAI API Error

**Issue**: `AuthenticationError` or `Rate limit exceeded`

**Solution**:
1. Check if `OPENAI_API_KEY` in `.env` file is correct
2. Confirm OpenAI account has balance
3. If rate limit exceeded, wait a few minutes and retry

### Discussion Not Updating in Real-time

**Issue**: Messages do not display in real-time

**Reason**: Current message interception mechanism is a temporary implementation; AutoGen output needs deeper integration

**Temporary Solution**: Refresh the page after discussion completes to view full history

## 🚀 Future Optimization Suggestions

1. **Real-time Message Push Optimization**
   - Current: AutoGen executes synchronously, message interception is difficult
   - Improvement: Implement AutoGen message hooks or use streaming output

2. **User Interaction Enhancement**
   - Allow users to join discussion mid-way
   - Support custom AI roles and personas
   - Adjust discussion rounds and search strategies

3. **Deployment Optimization**
   - Docker containerization
   - Use PostgreSQL instead of SQLite
   - Add user authentication system

4. **Performance Optimization**
   - Asynchronous discussion task processing
   - Cache search results
   - Message pagination loading

## 📄 License

MIT License

## 🤝 Contribution

Issues and Pull Requests are welcome!

---

**Warning**: Please be sure to protect your OpenAI API key and do not leak it to public code repositories!

