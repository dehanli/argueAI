import os
from dotenv import load_dotenv
from agents import DebateManager

load_dotenv()

# Test the emotion tagging
manager = DebateManager(os.getenv("OPENAI_API_KEY"))
manager.start_debate("Should we build a parking lot by the lake?")

print("=== Testing Emotion-Tagged Debate ===\n")

for i in range(3):
    agent_name, text = manager.next_turn()
    print(f"{agent_name}:")
    print(f"{text}\n")
    print("-" * 60)
