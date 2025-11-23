import os
from dotenv import load_dotenv
from fish_audio_service import FishAudioService

load_dotenv()

# Test emotion functionality
service = FishAudioService(os.getenv("FISH_AUDIO_API_KEY"))

test_cases = [
    ("I am happy today!", "happy"),
    ("I am sad about this situation.", "sad"),
    ("This makes me angry!", "angry"),
    ("I feel calm and peaceful.", "calm"),
]

print("=== Testing Fish Audio Emotions ===\n")

for text, emotion in test_cases:
    print(f"Text: {text}")
    print(f"Emotion: {emotion}")
    
    audio_file = service.generate_speech(text, voice_id=None, emotion=emotion)
    file_size = os.path.getsize(audio_file)
    
    print(f"✓ Generated: {audio_file}")
    print(f"  Size: {file_size} bytes")
    print()

print("All emotion tests completed!")
print("\nPlease listen to the generated audio files to verify emotions are working.")
