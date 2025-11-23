import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing o1-mini model...")

try:
    response = client.chat.completions.create(
        model="o1-mini",
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
        max_completion_tokens=100
    )
    print("✓ o1-mini works!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ o1-mini error: {e}")
    print("\nTrying gpt-5.1 instead...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[{"role": "user", "content": "Say hello in one sentence."}],
            max_completion_tokens=50
        )
        print("✓ gpt-5.1 works!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e2:
        print(f"✗ gpt-5.1 error: {e2}")
