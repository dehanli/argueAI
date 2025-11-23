import os
from dotenv import load_dotenv
from agents import DebateManager
from fish_audio_service import FishAudioService

load_dotenv()

# Test with the new emotion system
manager = DebateManager(os.getenv("OPENAI_API_KEY"))
fish_audio = FishAudioService(os.getenv("FISH_AUDIO_API_KEY"))

manager.start_debate("Should we build a parking lot by the lake?")

print("=== Testing Corrected Emotion System ===\n")

agent_name, text, emotion = manager.next_turn()
print(f"{agent_name}:")
print(f"Text (clean, no tags): {text}")
print(f"Emotion (API parameter): {emotion}\n")

# Test audio generation with emotion
print("Generating audio with emotion...")
audio_file = fish_audio.generate_speech(text, None, emotion)
print(f"✓ Audio generated: {audio_file}")
print(f"  File size: {os.path.getsize(audio_file)} bytes")
