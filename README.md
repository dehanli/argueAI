# EchoSystem

Simulating complex decisions through the voices of the environment.

## Creative Direction: Animism

To be truly creative, we need to break the "Human vs Human" or "Human vs Expert" mindset. We need to let Agents play roles that **"would absolutely never speak usually"**, or simulate those **"invisible"** social dynamics.

Here is a crazier, more artistic, and philosophically deep Social Good creative idea:

### Animism

*   **Pain Point**: When humans make decisions (like urban planning, environmental protection), they are often anthropocentric. We cannot hear the voice of nature, the voice of buildings, the voice of the future.
*   **Social Good**: Environmental protection, sustainable development, urban humanistic care.
*   **Core Concept**: Give voice to the voiceless.
*   **Agent Setting (The most Creative point)**: Agents no longer play "people", but play **"objects" or "concepts"**.

**Scenario**: For example, "Madison City wants to build a new parking lot by the lake".

*   **Agent A (Lake Mendota)**: Voice deep, surging (Fish Audio processing), it cares about water quality and ecology.
*   **Agent B (A 100-year-old tree here)**: Voice old, slow, it has witnessed history, cares about root systems and birds.
*   **Agent C (Future autonomous car)**: Voice mechanical, rushed, it thinks parking lots are outdated concepts, should build pick-up/drop-off points.

**User Experience**: Users input a social issue, and what they see is not two politicians arguing, but the entire ecosystem debating.

**Fish Audio Usage**: Must modulate completely different timbres for "lake water", "old tree", "concrete" to create a magical realism epic feel.


## Setup

1.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install openai python-dotenv
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```
    *(Note: The `.env` file is git-ignored to protect your credentials.)*

## Usage

Run the simulation using the virtual environment:
```bash
./venv/bin/python main.py
```

## TODO

Topics should not be hard coded, instead it should be selected by the user.

Build a frontend that can display two (or more) AI debating (like a group chat, using text bubble)

Incorporate Fish Audio at the end. 