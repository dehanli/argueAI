"""
Dynamic Role Generator - Automatically generate discussion roles based on topic
"""
import os
from openai import OpenAI

def generate_discussion_roles(topic: str, num_roles: int = 3):
    """
    Generate discussion roles based on topic

    Args:
        topic: Discussion topic
        num_roles: Number of roles to generate (default 3)

    Returns:
        list: List of roles, each containing name and system_message
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""You are an expert in generating discussion personas for debates.

The topic user wants to discuss is: "{topic}"

Please generate {num_roles} most suitable discussion roles/perspectives for this topic. These roles should:
1. View the topic from different standpoints and perspectives
2. Create interesting clashes of opinions and debates
3. Have short, powerful names (2-4 words)
4. Have clear standpoints and distinct personalities

Return in JSON format as follows:
{{
  "roles": [
    {{
      "name": "Role Name",
      "stance": "Brief description of the role's standpoint and perspective",
      "personality": "Character traits and speaking style"
    }}
  ]
}}

Example:
Topic: "Should we work overtime"
{{
  "roles": [
    {{
      "name": "Worker",
      "stance": "Firmly opposes meaningless overtime, believes work-life balance is important",
      "personality": "Straightforward, realistic, somewhat cynical, often complains"
    }},
    {{
      "name": "Startup CEO",
      "stance": "Believes hard work and dedication are necessary for success, moderate overtime is normal",
      "personality": "Passionate, pragmatic, results-oriented, good at motivating"
    }},
    {{
      "name": "Psychologist",
      "stance": "Focuses on mental health, advocates rational work, opposes rat race",
      "personality": "Gentle, rational, good listener, analyzes from psychological perspective"
    }}
  ]
}}

Now generate roles for the topic "{topic}". Return only JSON, nothing else."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        import json
        roles_data = json.loads(response.choices[0].message.content)

        # Convert to Agent format
        agents_config = []
        for role in roles_data.get("roles", []):
            # Clean name: remove spaces and special characters, replace with underscores (OpenAI API requirement)
            clean_name = role['name'].replace(' ', '_').replace('<', '').replace('>', '').replace('|', '').replace('/', '').replace('\\', '')

            system_message = f"""You are {role['name']}.

Your stance: {role['stance']}

Your personality: {role['personality']}

Discussion rules:
1. Stick to your position, view the issue from your perspective
2. When others share opinions (including users named "You"), you should:
   - If you agree, explain why and add your perspective
   - If you disagree, directly challenge and refute
   - Use "@[name]" to directly respond to someone (e.g., "@You", "@John")
   - Pay special attention to users' questions and respond actively
3. Keep it brief and powerful (2-3 sentences)
4. Show your personality, speak in character

【IMPORTANT】Emotion Expression Requirement:
You MUST start each reply with an emotion marker in the format: (emotion) text content
The emotion marker MUST be at the very beginning of your response.

SPEAK IN ENGLISH. Available emotion markers (Fish Audio S1 supported):
- Basic: (happy), (sad), (angry), (excited), (calm), (nervous), (confident), (surprised)
- Advanced: (satisfied), (delighted), (scared), (worried), (frustrated), (empathetic), (proud), (curious), (sarcastic)
- Tones: (whispering), (shouting), (soft tone)
- Effects: (laughing), (chuckling), (sighing), (gasping)

Example replies:
(angry) @John, your argument is completely flawed!
(excited) I totally agree! That's exactly the key point.
(sighing) You all are missing the real issue here...
(laughing) Ha ha ha! That idea is way too naive.
(curious) Hmm, let me think about this from another angle...

Always add the most appropriate emotion marker at the start of each response."""

            agents_config.append({
                "name": clean_name,  # Use cleaned name
                "display_name": role["name"],  # Keep original name for display
                "system_message": system_message,
                "stance": role["stance"],
                "personality": role["personality"]
            })

        return agents_config

    except Exception as e:
        print(f"rolegeneratefailed: {e}")
        # Fallback: return generic roles (names already cleaned, meet API requirements)
        return [
            {
                "name": "Supporter",
                "display_name": "Supporter",
                "system_message": """You support this topic and view it from a positive perspective. Keep it brief (2-3 sentences), show your stance.

【IMPORTANT】SPEAK IN ENGLISH. Each reply MUST start with an emotion marker at the very beginning, such as: (excited), (happy), (confident), (delighted), etc.""",
                "stance": "Supportive",
                "personality": "Positive, optimistic"
            },
            {
                "name": "Critic",
                "display_name": "Critic",
                "system_message": """You oppose this topic and view it from a critical perspective. Keep it brief (2-3 sentences), show your stance.

【IMPORTANT】SPEAK IN ENGLISH. Each reply MUST start with an emotion marker at the very beginning, such as: (angry), (frustrated), (sarcastic), (worried), etc.""",
                "stance": "Critical",
                "personality": "Critical, rational"
            },
            {
                "name": "Mediator",
                "display_name": "Mediator",
                "system_message": """You remain neutral and objectively analyze both sides' viewpoints. Keep it brief (2-3 sentences), show your stance.

【IMPORTANT】SPEAK IN ENGLISH. Each reply MUST start with an emotion marker at the very beginning, such as: (calm), (curious), (empathetic), etc.""",
                "stance": "Neutral",
                "personality": "Rational, objective"
            }
        ]
