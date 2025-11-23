import json
from openai import OpenAI

# Fish Audio supported emotions
FISH_EMOTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent"]

def detect_language(topic: str) -> str:
    """
    Detect if the topic is in Chinese or English.
    Returns 'zh' for Chinese, 'en' for English.
    """
    # Simple heuristic: if contains Chinese characters, it's Chinese
    for char in topic:
        if '\u4e00' <= char <= '\u9fff':
            return 'zh'
    return 'en'

def generate_landscape_objects(topic: str, client: OpenAI, num_objects: int = 3) -> list:
    """
    Use OpenAI to generate relevant landscape objects based on the topic.
    
    Args:
        topic: The debate topic
        client: OpenAI client instance
        num_objects: Number of objects to generate
        
    Returns:
        List of object dictionaries with name, type, and description
    """
    lang = detect_language(topic)
    lang_instruction = "用中文回答" if lang == 'zh' else "Answer in English"
    
    prompt = f"""Given this topic: "{topic}"

Generate {num_objects} landscape objects (non-living things like lakes, mountains, buildings, streets, air, etc.) that would have a perspective on this topic.

Consider:
1. Geographic context from the topic
2. Environmental elements related to the topic
3. Man-made structures if relevant

{lang_instruction}. Return a JSON array with this format:
[
  {{
    "name": "Object name",
    "type": "object type (lake/mountain/building/etc)",
    "description": "Brief description including location if applicable"
  }}
]

Only return the JSON array, no other text."""

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_completion_tokens=500
    )
    
    result_text = response.choices[0].message.content.strip()
    
    # Extract JSON from response
    try:
        # Try to parse directly
        objects = json.loads(result_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if "```json" in result_text:
            json_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_text = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_text = result_text
        objects = json.loads(json_text)
    
    return objects


def generate_agent_personality(object_info: dict, topic: str, client: OpenAI) -> dict:
    """
    Generate an agent personality for a landscape object using OpenAI.
    
    Args:
        object_info: Dictionary with name, type, description
        topic: The debate topic
        client: OpenAI client instance
        
    Returns:
        Agent configuration dict with name, role, voice_id, emotions
    """
    lang = detect_language(topic)
    lang_instruction = "用中文回答" if lang == 'zh' else "Answer in English"
    
    prompt = f"""You are creating an agent personality for a conversation simulation.

Object Information:
- Name: {object_info['name']}
- Type: {object_info['type']}
- Description: {object_info['description']}

Topic: "{topic}"

Create a personality where this object speaks as "I" (first person), as if it has come to life and has its own perspective.

Consider:
1. What would this object experience and feel?
2. How would it view the topic from its unique position?
3. What would it care about based on its nature?

IMPORTANT: The personality description should be written from the object's perspective, using first person ("I am...", "I care about...").

EMOTIONS: You must choose 2-3 emotions from this list ONLY: {", ".join(FISH_EMOTIONS)}

{lang_instruction}. Return ONLY a JSON object with this exact format:
{{
  "name": "The object's name",
  "role": "Personality from first-person perspective (2-3 sentences). Start with 'I am...' or 'I'm...'. Describe what you experience, what you care about.",
  "emotions": ["emotion1", "emotion2"]
}}"""

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,  # Lower temperature for more consistent, less creative responses
        max_completion_tokens=300
    )
    
    result_text = response.choices[0].message.content.strip()
    
    # Extract JSON
    try:
        agent_config = json.loads(result_text)
    except json.JSONDecodeError:
        if "```json" in result_text:
            json_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_text = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_text = result_text
        agent_config = json.loads(json_text)
    
    # Validate emotions
    valid_emotions = [e for e in agent_config.get("emotions", []) if e in FISH_EMOTIONS]
    if not valid_emotions:
        valid_emotions = ["calm"]  # Default fallback
    
    return {
        "name": agent_config["name"],
        "role": agent_config["role"],
        "voice_id": None,
        "emotions": valid_emotions[:3]  # Limit to 3 emotions
    }


def generate_agents_from_topic(topic: str, client: OpenAI, num_agents: int = 3) -> list:
    """
    Main function to generate agents from a topic.
    
    Args:
        topic: The debate topic
        client: OpenAI client instance
        num_agents: Number of agents to generate
        
    Returns:
        List of agent configuration dictionaries
    """
    # Step 1: Generate landscape objects
    objects = generate_landscape_objects(topic, client, num_agents)
    
    # Step 2: Generate agent personalities for each object
    agents = []
    for obj in objects:
        try:
            agent = generate_agent_personality(obj, topic, client)
            agents.append(agent)
        except Exception as e:
            print(f"Error generating agent for {obj.get('name', 'unknown')}: {e}")
            # Continue with other agents
            continue
    
    return agents
