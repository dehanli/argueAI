# Brainstormer

## Inspiration
In an era where technical barriers are lower than ever, the real competitive advantage lies in ideas, not implementation.

But here's the paradox: when you brainstorm with a single AI, you're trapped in a single context thread. Every response builds on the same perspective, creating an echo chamber rather than true multi-dimensional thinking.

Traditional AI chat can refine your ideas, but it cannot challenge them from fundamentally different worldviews. You need conflicting perspectives to stress-test an idea—and that's what **BrainStormer** delivers.

## What it does
BrainStormer is a multi-agent brainstorming platform that simulates a "podcast-style" debate between three distinct AI personas, each with a unique worldview and voice:

**Dynamic Agent Generation**: Agents are automatically generated based on the topic input to ensure the most relevant perspectives.
*   **Fallback Personas**: In case agent generation fails, the system defaults to:
    1.  **The Philosopher**: Deep, Socratic, and focused on ethics and first principles.
    2.  **The Scientist**: Empirical, skeptical, and demanding of evidence.
    3.  **The Artist**: Intuitive, emotional, and focused on human experience.

Users provide a topic (e.g., "Will AI replace creativity?"), and these agents engage in a dynamic, voice-enabled discussion. They don't just take turns; they interrupt, agree, challenge, and build upon each other using our **Intelligent Turn-Taking System**.

Key features:
*   **Multi-Perspective Debate**: Agents are forced to disagree and challenge assumptions.
*   **Real-Time Web Search**: Agents use DuckDuckGo to pull in real-world facts to support their arguments.
*   **Distinct Voices**: Integrated **Fish Audio** TTS gives each agent a unique, emotive voice.
*   **Dynamic Flow**: No robotic round-robin. An LLM orchestrator decides who speaks next based on conversation flow and "drama".

## How we built it
We moved away from a complex microservices architecture to a streamlined, high-performance monolith.

*   **Core Engine**: Python & **FastAPI**.
*   **Agent Orchestration**: **Microsoft AutoGen**. We customized the `ConversableAgent` to enforce strict persona boundaries.
*   **Intelligence**: **GPT-4o-mini** for both agent responses and the orchestration logic.
*   **Voice**: **Fish Audio API**. We use their high-fidelity TTS to generate distinct voices for each persona (e.g., "Energetic Male" for the Scientist, "Sarah" for the Artist).
*   **Search**: **DuckDuckGo Search** tool integration allows agents to ground their arguments in reality.
*   **Frontend**: Jinja2 Templates + Vanilla JS for a lightweight, responsive UI that updates in real-time via **WebSockets**.

## Challenges we ran into
*   **The "Politeness" Problem**: Initially, the agents were too nice to each other. They would constantly say "I agree with you." We had to rigorously tune the system prompts to encourage conflict, skepticism, and "intellectual collision."
*   **Robotic Turn-Taking**: A simple loop (A -> B -> C) felt unnatural. We built a custom `_select_next_speaker` function that analyzes the last few turns and decides who *should* speak next to maximize engagement, or if the user was addressed directly.
*   **Latency vs. Quality**: Generating high-quality audio takes time. We optimized this by using Fish Audio's "balanced" latency mode and processing audio generation asynchronously while the text is being displayed.

## Accomplishments that we're proud of
*   **"It feels alive"**: The combination of the intelligent turn-taking and the emotive voices makes the conversation feel like a real podcast.
*   **Voice Cloning**: We successfully implemented a feature to clone voices, allowing for potentially infinite custom personas.
*   **Simplified Architecture**: We successfully refactored the project from a split React/Python repo into a single, easy-to-deploy FastAPI application without losing functionality.

## What we learned
*   **Context is King**: Managing the context window for multiple agents is tricky. We learned to summarize and truncate history effectively to keep the debate focused.
*   **Voice Changes Perception**: The exact same text is perceived completely differently depending on the voice. A "Scientist" voice makes a statement sound like a fact, while a "Philosopher" voice makes it sound like a theory.

## What's next for Brainstormer
*   **Visual Avatars**: Adding lip-syncing 3D or 2D avatars to match the voices.
*   **User Voice Intervention**: Allowing the user to interrupt the debate with their own voice (Speech-to-Text).
*   **Export to Podcast**: One-click generation of an MP3 file of the entire debate to listen to on the go.
*   **More Roles**: Adding an "Economist", "Historian", or "Futurist" to the roster.

---

## 🛠 Installation & Run

### Prerequisites
- Python 3.9+
- OpenAI API Key
- Fish Audio API Key (optional, for TTS)

### Setup

1.  **Clone the repo**
    ```bash
    git clone <repo-url>
    cd argueAI
    ```

2.  **Install dependencies**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file:
    ```env
    OPENAI_API_KEY=your_key_here
    FISH_AUDIO_API_KEY=your_fish_audio_key  # Optional
    ```

4.  **Run**
    ```bash
    python src/main.py
    ```
    Visit `http://localhost:8000` to start brainstorming!
