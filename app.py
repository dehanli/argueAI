import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
from agents import DebateManager
from fish_audio_service import FishAudioService

load_dotenv()

app = Flask(__name__)

# Initialize services
fish_audio = FishAudioService(api_key=os.getenv("FISH_AUDIO_API_KEY"))
debate_manager = DebateManager(openai_api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_debate', methods=['POST'])
def start_debate():
    data = request.json
    topic = data.get('topic')
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    debate_manager.start_debate(topic)
    return jsonify({"status": "started", "topic": topic})

@app.route('/next_turn', methods=['POST'])
def next_turn():
    try:
        # Get the next agent's response
        agent_name, text = debate_manager.next_turn()
        
        if not text:
            return jsonify({"status": "finished"})

        # Generate audio
        # We use a simple mapping or the agent's internal ID to pick a voice
        voice_id = debate_manager.get_agent_voice_id(agent_name)
        audio_filename = fish_audio.generate_speech(text, voice_id)
        
        return jsonify({
            "status": "ongoing",
            "agent": agent_name,
            "text": text,
            "audio_url": f"/audio/{os.path.basename(audio_filename)}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    # Ensure audio directory exists
    os.makedirs('static/audio', exist_ok=True)
    app.run(debug=True, port=5002)
