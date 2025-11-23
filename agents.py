from openai import OpenAI
from agent_generator import generate_agents_from_topic, detect_language

class DebateManager:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.topic = None
        self.history = []
        self.current_agent_index = 0
        self.debate_language = 'en'  # Track debate language
        
        # Agents will be generated dynamically based on topic
        self.agents = []

    def start_debate(self, topic):
        """Initialize debate and generate agents from topic"""
        self.topic = topic
        self.history = []
        self.current_agent_index = 0
        
        # Detect language from topic
        self.debate_language = detect_language(topic)
        
        # Generate agents dynamically from the topic
        print(f"Generating agents for topic: {topic}")
        self.agents = generate_agents_from_topic(topic, self.client, num_agents=3)
        print(f"Generated {len(self.agents)} agents: {[a['name'] for a in self.agents]}")

    def next_turn(self):
        if not self.topic:
            raise ValueError("Debate not started")

        agent = self.agents[self.current_agent_index]
        
        # Build context with language instruction for deeper thinking
        if self.debate_language == 'zh':
            thinking_prompt = """深入思考以下几个方面：
1. 从我作为{name}的独特视角看，这个话题如何影响我？
2. 我与其他发言者的观点有什么不同？为什么？
3. 基于我的本质和经历，我最关心什么？

用第一人称'我'说话，表达2-3句深思熟虑的观点。不要夸张或戏剧化。"""
        else:
            thinking_prompt = """Think deeply about:
1. How does this topic affect me specifically as {name}?
2. How do I differ from the other speakers, and why?
3. What do I care most about, based on my nature and experience?

Speak as 'I' in first person. Share 2-3 thoughtful sentences. Be natural, not dramatic."""
        
        # Build system message
        system_prompt = f"""You are {agent['name']}.

Your nature: {agent['role']}

Topic being discussed: {self.topic}

{thinking_prompt.format(name=agent['name'])}"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if self.history:
            history_text = "Previous conversation:\n"
            for turn in self.history:
                history_text += f"- {turn['agent']}: {turn['text']}\n"
            messages.append({"role": "user", "content": history_text})
        
        # Ask for response
        messages.append({"role": "user", "content": f"Now share your perspective as {agent['name']}:"})

        # Use gpt-5.1 with settings optimized for thoughtful responses
        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            max_completion_tokens=400,  # Allow for detailed thinking
            temperature=0.9  # Higher for more creative, thoughtful responses
        )
        
        text = response.choices[0].message.content
        
        # Select an emotion for this response
        emotion = self._select_emotion(agent)
        
        # Update history with original text
        self.history.append({"agent": agent['name'], "text": text})
        
        # Rotate turn
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
        
        return agent['name'], text, emotion

    def get_agent_voice_id(self, agent_name):
        for agent in self.agents:
            if agent['name'] == agent_name:
                return agent['voice_id']
        return None
    
    def _select_emotion(self, agent):
        """
        Select an emotion for the agent based on their emotion palette.
        Returns a Fish Audio supported emotion string.
        """
        import random
        return random.choice(agent['emotions'])
