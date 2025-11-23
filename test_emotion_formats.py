import os
from dotenv import load_dotenv
from fish_audio_sdk import Session, TTSRequest

load_dotenv()

api_key = os.getenv("FISH_AUDIO_API_KEY")
session = Session(api_key)

# Test different emotion formats
test_cases = [
    "Hello, I am the lake.",  # No emotion
    "(sad) I am disappointed by this decision.",  # Emotion at start
    "[sad] I am disappointed by this decision.",  # Brackets instead
    "I am disappointed by this decision. [sad]",  # Emotion at end
]

for i, text in enumerate(test_cases):
    print(f"Test {i+1}: {text}")
    try:
        request = TTSRequest(text=text)
        output_file = f"emotion_test_{i+1}.mp3"
        with open(output_file, "wb") as f:
            for chunk in session.tts(request):
                f.write(chunk)
        print(f"  ✓ Generated {output_file}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
