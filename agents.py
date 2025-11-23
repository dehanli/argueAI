from openai import OpenAI

class DebateManager:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.topic = None
        self.history = []
        self.current_agent_index = 0
        
        # Define agents with their specific personalities
        # Using default Fish Audio voice for all agents (voice_id=None)
        # In the future, you can specify different reference_ids for each agent
        self.agents = [
            {
                "name": "Lake Mendota",
                "role": "The spirit of the lake. Deep, surging voice. Cares about water quality, ecology, and the long-term health of the environment. Skeptical of human construction.",
                "voice_id": None
            },
            {
                "name": "Old Oak Tree",
                "role": "A 100-year-old tree. Slow, ancient voice. Witness to history. Cares about root systems, birds, and stability. Dislikes rapid change.",
                "voice_id": None
            },
            {
                "name": "Future Autonomous Car",
                "role": "A sentient vehicle from 2050. Mechanical, rushed, efficient voice. Thinks traditional infrastructure is outdated. Wants smart, flexible solutions.",
                "voice_id": None
            }
        ]

    def start_debate(self, topic):
        self.topic = topic
        self.history = []
        self.current_agent_index = 0
        # Initial system context could be set here if needed

    def next_turn(self):
        if not self.topic:
            raise ValueError("Debate not started")

        agent = self.agents[self.current_agent_index]
        
        # Build context
        system_prompt = f"You are {agent['name']}. {agent['role']} You are debating the topic: '{self.topic}'."
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for turn in self.history:
            messages.append({"role": "user", "content": f"{turn['agent']} said: {turn['text']}"})
            
        messages.append({"role": "user", "content": "Express your opinion on the topic and respond to previous speakers. Keep it under 3 sentences. Be characterful."})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        
        text = response.choices[0].message.content
        
        # Update history
        self.history.append({"agent": agent['name'], "text": text})
        
        # Rotate turn
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
        
        return agent['name'], text

    def get_agent_voice_id(self, agent_name):
        for agent in self.agents:
            if agent['name'] == agent_name:
                return agent['voice_id']
        return None
