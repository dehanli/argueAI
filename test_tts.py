import os
from dotenv import load_dotenv
from fish_audio_sdk import Session, TTSRequest

load_dotenv()

api_key = os.getenv("FISH_AUDIO_API_KEY")
if not api_key:
    print("Error: FISH_AUDIO_API_KEY not found.")
    exit(1)

session = Session(api_key)

# Test TTS without specifying a reference_id (use default voice)
try:
    print("Testing TTS with default voice...")
    request = TTSRequest(
        text="Hello, I am the spirit of Lake Mendota.",
        reference_id=None  # Try without reference_id first
    )
    
    # Try to generate audio
    output_file = "test_output.mp3"
    with open(output_file, "wb") as f:
        for chunk in session.tts(request):
            f.write(chunk)
    
    print(f"Success! Audio saved to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying without reference_id parameter...")
    
    try:
        request = TTSRequest(text="Hello, I am the spirit of Lake Mendota.")
        with open("test_output2.mp3", "wb") as f:
            for chunk in session.tts(request):
                f.write(chunk)
        print("Success with simpler request!")
    except Exception as e2:
        print(f"Also failed: {e2}")
