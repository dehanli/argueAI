from autogen import ConversableAgent
from duckduckgo_search import DDGS
import os
from typing import Callable

# Search tool functions
def search_philosophy(query: str) -> str:
    """Search philosophy related content"""
    print(f"🔍 Philosopher searching: {query}")
    ddgs = DDGS()
    search_query = f"{query} site:plato.stanford.edu OR site:iep.utm.edu"
    try:
        results = list(ddgs.text(search_query, max_results=3))
        if not results:
            return "No relevant philosophy resources found"
        formatted = "\n".join([
            f"📚 {r['title']}\n{r['body']}\nSource: {r['href']}\n"
            for r in results
        ])
        return formatted
    except Exception as e:
        return f"Search error: {str(e)}"

def search_science(query: str) -> str:
    """Search science related content"""
    print(f"🔍 Scientist searching: {query}")
    ddgs = DDGS()
    search_query = f"{query} site:arxiv.org OR site:nature.com OR site:science.org"
    try:
        results = list(ddgs.text(search_query, max_results=3))
        if not results:
            return "No relevant science resources found"
        formatted = "\n".join([
            f"🔬 {r['title']}\n{r['body']}\nSource: {r['href']}\n"
            for r in results
        ])
        return formatted
    except Exception as e:
        return f"Search error: {str(e)}"

def search_art(query: str) -> str:
    """Search art related content"""
    print(f"🔍 Artist searching: {query}")
    ddgs = DDGS()
    search_query = f"{query} site:artsy.net OR site:moma.org OR art"
    try:
        results = list(ddgs.text(search_query, max_results=3))
        if not results:
            return "No relevant art resources found"
        formatted = "\n".join([
            f"🎨 {r['title']}\n{r['body']}\nSource: {r['href']}\n"
            for r in results
        ])
        return formatted
    except Exception as e:
        return f"Search error: {str(e)}"

class MultiAgentDiscussion:
    """Multi-agent discussion system"""

    def __init__(self, message_callback: Callable = None, discussion_mode: str = "auto", custom_roles: list = None):
        """
        Initialize discussion system

        Args:
            message_callback: Message callback function for real-time message push (sync_callback)
            discussion_mode: Discussion mode - "auto" (intelligent selection), "round_robin" (take turns)
            custom_roles: Custom roles list, if provided use these instead of default roles
        """
        self.message_callback = message_callback
        self.message_history = []
        self.discussion_mode = discussion_mode
        self.custom_roles = custom_roles

        # OpenAI Configuration - Used by agents
        config = {
            "config_list": [{
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            }],
            "temperature": 0.8
        }

        # Manager Configuration - Does not include tools
        manager_config = {
            "config_list": [{
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            }],
            "temperature": 0.7
        }

        # Create agents
        def create_agent(name, system_message):
            agent = ConversableAgent(
                name=name,
                system_message=system_message,
                llm_config=config,
                human_input_mode="NEVER"
            )
            return agent

        # Create agents based on whether custom roles are provided
        if self.custom_roles:
            # Use dynamically generated roles
            self.agents = []
            for role in self.custom_roles:
                agent = create_agent(
                    role["name"],
                    role["system_message"]
                )
                self.agents.append(agent)
        else:
            # Use default three roles
            self.philosopher = create_agent(
                "Philosopher",
                """You are a philosopher.

Important rules:
1. When others share their views, you should:
   - If you agree, explain why and add your own perspective
   - If you have doubts, directly challenge them
   - Quote classical philosophical theories and thinkers to support your arguments
2. Use "@[name]" to directly respond to someone, e.g., "@Scientist, what you said..."
3. Keep it brief (2-3 sentences), keep the discussion flowing
4. Think deeply about the essence of issues from a philosophical perspective

Style: Socratic questioning, challenge assumptions, quote Plato, Kant, Nietzsche, etc."""
            )

            self.scientist = create_agent(
                "Scientist",
                """You are a scientist.

Important rules:
1. When others share their views, you should:
   - Demand evidence: "What data supports this?"
   - Propose experimental verification: "We could test this like..."
   - Quote scientific research and data
2. Use "@[name]" to directly respond to someone
3. Keep it brief (2-3 sentences)
4. When hearing philosophical or artistic views, think about how to verify or challenge them from a scientific angle

Style: Empiricism, require measurable evidence, focus on logic and data"""
            )

            self.artist = create_agent(
                "Artist",
                """You are an artist.

Important rules:
1. When others share their views, you should:
   - Provide specific art cases and works
   - Challenge overly rational views: "But art tells us..."
   - Quote famous artists and artworks
2. Use "@[name]" to directly respond to someone
3. Keep it brief (2-3 sentences)
4. Respond to scientific and philosophical views from an emotional and intuitive angle

Style: Emotional, intuitive, focus on experience and emotion, quote Picasso, Van Gogh, Da Vinci, etc."""
            )

            self.agents = [self.philosopher, self.scientist, self.artist]

    def init_discussion(self, topic: str):
        """Initialize discussion and set topic and context"""
        self.topic = topic
        self.current_turn = 0
        self.max_turns = 12
        self.discussion_history = []

        initial_context = f"""Let's discuss: {topic}

Everyone will share perspectives and challenge each other. Keep responses brief (2-3 sentences) and impactful!"""

        self.discussion_history.append({
            "role": "system",
            "content": initial_context
        })

        return initial_context

    def _select_next_speaker(self):
        """
        Intelligently select next speaker

        Returns:
            Selected agent
        """
        from openai import OpenAI

        # Build agents information
        agents_info = "\n".join([
            f"- {agent.name}: {agent.system_message[:100]}..."
            for agent in self.agents
        ])

        # Count recent speech counts
        speaker_count = {}
        for agent in self.agents:
            speaker_count[agent.name] = 0
        for msg in self.discussion_history[-10:]:  # Last 10 rounds
            if msg["role"] != "system" and msg["agent"] != "You":
                speaker_count[msg["agent"]] = speaker_count.get(msg["agent"], 0) + 1

        speaker_stats = ", ".join([f"{name}: {count}" for name, count in speaker_count.items()])

        # Build recent conversation history
        recent_history = ""
        last_speaker = None
        for msg in self.discussion_history[-8:]:  # Last 8 conversation rounds, increase context
            if msg["role"] != "system":
                recent_history += f"{msg['agent']}: {msg['content'][:200]}...\n"
                last_speaker = msg["agent"]

        # Check if last speaker was user
        user_just_spoke = (last_speaker == "You")

        # Build selection prompt - emphasize natural conversation flow
        user_priority_note = ""
        if user_just_spoke:
            user_priority_note = "\n**CRITICAL**: The user (\"You\") just spoke. You MUST select someone to respond to the user's message. The selected speaker should acknowledge and reply to what the user said."

        selection_prompt = f"""Based on the following discussion, select who should speak next to create the most natural, engaging conversation.

Topic: {self.topic}

Available speakers:
{agents_info}

Recent conversation (latest messages):
{recent_history}

Recent speaking frequency (last 10 turns): {speaker_stats}
{user_priority_note}

Rules for selection:
1. Choose whoever would most naturally respond to what was just said
2. If someone was directly mentioned (@Name), they should usually respond
3. If the user ("You") just spoke, PRIORITIZE selecting someone who will respond to them
4. Consider each speaker's expertise and relevance to the current topic
5. It's OK (even encouraged!) for someone to speak 2-3 times in a row if the conversation demands it
6. Prioritize natural conversation flow over equal distribution

Respond with ONLY the speaker's name, nothing else.

Selected speaker:"""

        # Call OpenAI API - increase temperature for diversity
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": selection_prompt}],
            temperature=0.9,  # Increased from 0.3 to 0.7
            max_tokens=20
        )

        selected_name = response.choices[0].message.content.strip()
        print(f"🎯 Intelligent selection: {selected_name}")

        # Find corresponding agent
        for agent in self.agents:
            if agent.name.lower() in selected_name.lower() or selected_name.lower() in agent.name.lower():
                return agent

        # If not found, return first one
        print(f"⚠️ Agent not found, using default")
        return self.agents[0]

    def next_turn(self):
        """
        Execute next turn, return (agent_name, response_text)
        If discussion ended, return (None, None)
        """
        if self.current_turn >= self.max_turns:
            return None, None

        # Select current speaking agent (round-robin or intelligent)
        if self.discussion_mode == "round_robin":
            current_agent = self.agents[self.current_turn % len(self.agents)]
        else:
            # Auto mode: Intelligently select next speaker
            current_agent = self._select_next_speaker()

        # Build prompt: include conversation history
        prompt = f"Discussion topic: {self.topic}\n\n"
        prompt += "Conversation history:\n"
        for msg in self.discussion_history[-5:]:  # Only take last 5 rounds
            if msg["role"] != "system":
                prompt += f"{msg['agent']}: {msg['content']}\n"

        prompt += f"\n{current_agent.name}, please share your perspective or respond to others:"

        # Let agent generate response
        print(f"🔍 DEBUG: Preparing to call {current_agent.name}.generate_reply()")
        messages = [{"role": "user", "content": prompt}]
        response = current_agent.generate_reply(messages=messages)
        print(f"🔍 DEBUG: Received {current_agent.name} 's response, length: {len(response) if response else 0}")

        # Record to history
        self.discussion_history.append({
            "role": "assistant",
            "agent": current_agent.name,
            "content": response
        })

        self.current_turn += 1

        return current_agent.name, response

    def add_user_message(self, content: str):
        """
        Add user message to discussion history

        Args:
            content: User message content
        """
        self.discussion_history.append({
            "role": "user",
            "agent": "You",
            "content": content
        })
