import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define agents
agents = [
    {"name": "Alice", "role": "an optimistic philosopher", "history": []},
    {"name": "Bob", "role": "a cautious scientist", "history": []},
    {"name": "Carol", "role": "a creative artist", "history": []}
]

def chat(agent, topic, conversation_history):
    """Let the agent speak based on conversation history"""
    # Build system prompt
    system_prompt = f"You are {agent['name']}, {agent['role']}. Participating in a multi-person discussion."

    # Build messages
    messages = [{"role": "system", "content": system_prompt}] + conversation_history + [
        {"role": "user", "content": f"Current topic: {topic}\nPlease express your opinion (keep it short, 2-3 sentences)"}
    ]

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=messages,
        max_completion_tokens=200
    )

    return response.choices[0].message.content

# Main loop
topic = "Will AI replace human creativity?"
conversation_history = []
rounds = 5

print(f"Topic: {topic}\n{'='*50}\n")

for round in range(rounds):
    print(f"\n--- Round {round+1} ---\n")

    for agent in agents:
        # Agent speaks
        response = chat(agent, topic, conversation_history)

        # Print
        print(f"{agent['name']}: {response}\n")

        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": f"{agent['name']} says: {response}"
        })
        # Note: In a real multi-agent chat, we might handle history differently, 
        # but appending previous turns as 'user' content is a simple way to simulate context for the next speaker.
        
        time.sleep(1)  # Avoid rate limits

print("\nConversation ended!")