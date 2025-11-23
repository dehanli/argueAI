import os
from dotenv import load_dotenv
from agent_generator import generate_agents_from_topic
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test with different topics
test_topics = [
    "Should we build a parking lot by Lake Mendota in Madison?",
    "How can we improve air quality in Beijing?",
    "The impact of urban development on natural ecosystems"
]

print("=== Testing Dynamic Agent Generation ===\n")

for topic in test_topics:
    print(f"Topic: {topic}")
    print("-" * 60)
    
    try:
        agents = generate_agents_from_topic(topic, client, num_agents=3)
        
        print(f"Generated {len(agents)} agents:\n")
        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent['name']}")
            print(f"   Role: {agent['role']}")
            print(f"   Emotions: {', '.join(agent['emotions'])}")
            print()
        
    except Exception as e:
        print(f"ERROR: {e}\n")
    
    print("=" * 60)
    print()
