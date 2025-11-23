"""
Fish Audio TTS Handler - HTTP API One-time Generation
"""
import os
import httpx
import msgpack
import base64
from typing import Optional

# Fish Audio available voice profiles (selected based on character traits)
# Real voice IDs from documentation - All support S1 emotion control
# Using Energetic Male for all to test emotion control consistency
VOICE_PROFILES = {
    "male_young": "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male - verified emotion control
    "male_mature": "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male (temp for testing)
    "female_young": "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male (temp for testing)
    "female_mature": "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male (temp for testing)
    "neutral": "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male (temp for testing)
}

def select_voice_for_role(role_name: str, personality: str) -> str:
    """
    Select appropriate voice based on role name and personality

    Args:
        role_name: Role name
        personality: Role personality description

    Returns:
        str: Voice ID
    """
    # Simple rule matching
    name_lower = role_name.lower()
    personality_lower = personality.lower()

    # Match by keywords (English keywords)
    if any(word in name_lower for word in ["boss", "expert", "professor", "mentor", "leader"]):
        return VOICE_PROFILES["male_mature"]
    elif any(word in name_lower for word in ["student", "young", "junior", "new"]):
        return VOICE_PROFILES["female_young"]
    elif any(word in personality_lower for word in ["gentle", "soft", "careful", "patient"]):
        return VOICE_PROFILES["female_mature"]
    elif any(word in personality_lower for word in ["passionate", "strong", "decisive", "direct"]):
        return VOICE_PROFILES["male_mature"]
    else:
        # Random assignment by default
        voices = list(VOICE_PROFILES.values())
        import random
        return random.choice(voices)


async def generate_tts(text: str, voice_id: str) -> Optional[str]:
    """
    Generate speech using Fish Audio HTTP API

    Args:
        text: Text to synthesize
        voice_id: Voice ID

    Returns:
        str: base64-encoded complete MP3 audio, None if failed
    """
    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        print("⚠️ FISH_AUDIO_API_KEY not found, skipping TTS")
        return None

    print(f"🎤 Starting TTS synthesis (voice: {voice_id}): {text[:80]}...")
    print(f"   📝 Full text for TTS: {repr(text)}")

    try:
        # Prepare request data
        request_data = {
            "text": text,
            "reference_id": voice_id,
            "format": "mp3",
            "mp3_bitrate": 128,
            "normalize": True,
            "latency": "balanced"  # Balanced mode, faster
        }

        # Send request - Use S1 model for emotion control support
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.fish.audio/v1/tts",
                content=msgpack.packb(request_data),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/msgpack",
                    "model": "s1"  # S1 model supports emotion tags like (happy), (sad), etc.
                }
            )

            if response.status_code == 200:
                # Convert to base64
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                print(f"✅ TTS generated successfully (size: {len(response.content)} bytes)")
                return audio_base64
            else:
                print(f"❌ TTS generation failed: {response.status_code} - {response.text}")
                return None

    except Exception as e:
        print(f"❌ TTS error: {e}")
        return None


async def create_voice_clone(name: str, audio_data: bytes, description: str = "") -> Optional[str]:
    """
    Create voice clone using Fish Audio Python SDK

    Uses voices.create() method to create persistent voice model

    Args:
        name: Voice name
        audio_data: Audio data (bytes)
        description: Voice description (optional)

    Returns:
        str: Created voice ID, None if failed
    """
    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        print("⚠️ FISH_AUDIO_API_KEY not found, cannot clone voice")
        return None

    print(f"🎙️ Starting voice clone creation: {name}")

    try:
        from fishaudio import FishAudio
        import asyncio

        # Create voice using Fish Audio Python SDK
        def create_voice_sync():
            client = FishAudio(api_key=api_key)

            # Create voice model
            voice = client.voices.create(
                title=name,
                voices=[audio_data],
                description=description or f"Custom voice clone: {name}",
                visibility="private"
            )

            return voice.id

        # Run sync function in thread pool
        loop = asyncio.get_event_loop()
        voice_id = await loop.run_in_executor(None, create_voice_sync)

        print(f"✅ Voice clone created successfully! Voice ID: {voice_id}")
        return voice_id

    except Exception as e:
        print(f"❌ Voice clone error: {e}")
        import traceback
        traceback.print_exc()
        return None
