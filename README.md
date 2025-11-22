# ArgueAI

A multi-agent discussion simulation using OpenAI's API.

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

Run the simulation:
```bash
python main.py
```
