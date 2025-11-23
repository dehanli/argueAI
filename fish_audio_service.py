import os
import uuid
from fish_audio_sdk import Session, TTSRequest

class FishAudioService:
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialize session if API key is present
        if self.api_key:
            self.session = Session(self.api_key)
        else:
            self.session = None
            print("Warning: No Fish Audio API key provided. Audio generation will be skipped/mocked.")

    def generate_speech(self, text, voice_id=None):
        """
        Generates speech for the given text.
        Returns the path to the saved audio file.
        Note: voice_id is currently ignored as we use the default voice.
        """
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join("static/audio", filename)
        
        # Ensure directory exists
        os.makedirs("static/audio", exist_ok=True)

        if not self.session:
            # Mock behavior if no API key
            print(f"[Mock] Generating audio for: {text[:30]}...")
            # Create a dummy file
            with open(filepath, "wb") as f:
                f.write(b"mock audio content")
            return filepath

        try:
            # Use the Fish Audio SDK with default voice
            # The TTSRequest can be created with just text
            request = TTSRequest(text=text, reference_id=voice_id) if voice_id else TTSRequest(text=text)
            
            with open(filepath, "wb") as f:
                for chunk in self.session.tts(request):
                    f.write(chunk)
                    
            return filepath
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Fallback to mock to prevent crash
            with open(filepath, "wb") as f:
                f.write(b"error placeholder")
            return filepath
