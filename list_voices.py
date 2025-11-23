import os
from dotenv import load_dotenv
from fish_audio_sdk import Session

load_dotenv()

api_key = os.getenv("FISH_AUDIO_API_KEY")
if not api_key:
    print("Error: FISH_AUDIO_API_KEY not found.")
    exit(1)

session = Session(api_key)

try:
    # Attempt to list models. The SDK documentation summary mentioned listing models.
    # If this specific method doesn't exist, we'll catch the error.
    # Common patterns: session.list_models(), session.models.list()
    
    # Based on search result "The SDK also supports listing models..."
    # Let's try listing and printing the first few.
    
    models = session.list_models()
    print(f"Listing models:")
    count = 0
    for model in models:
        print(f"Model {count}: {model.title} (ID: {model.id})")
        count += 1
        if count >= 5:
            break
        
except Exception as e:
    print(f"Error listing models: {e}")
    # Fallback: Print help or dir to see available methods if this fails
    print("Session methods:", dir(session))
