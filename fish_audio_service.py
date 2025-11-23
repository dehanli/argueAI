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

    def generate_speech(self, text, voice_id=None, emotion=None):
        """
        Generates speech for the given text.
        Returns the path to the saved audio file.
        
        Args:
            text: The text to convert to speech
            voice_id: Optional voice model ID
            emotion: Optional emotion (happy, sad, angry, fearful, disgusted, surprised, calm, fluent, auto)
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
            # Use the Fish Audio SDK with emotion parameter
            # Build TTSRequest with emotion if provided
            request_params = {"text": text}
            if voice_id:
                request_params["reference_id"] = voice_id
            if emotion:
                request_params["emotion"] = emotion
            
            request = TTSRequest(**request_params)
            
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
