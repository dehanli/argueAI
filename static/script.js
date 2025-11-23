document.addEventListener('DOMContentLoaded', () => {
    const setupPanel = document.getElementById('setup-panel');
    const debatePanel = document.getElementById('debate-panel');
    const startBtn = document.getElementById('start-btn');
    const nextTurnBtn = document.getElementById('next-turn-btn');
    const topicInput = document.getElementById('topic-input');
    const currentTopicText = document.getElementById('current-topic-text');
    const chatContainer = document.getElementById('chat-container');
    const statusIndicator = document.getElementById('status-indicator');

    // Suggested Topics Handler
    document.querySelectorAll('.topic-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            topicInput.value = chip.getAttribute('data-text');
            topicInput.focus();
        });
    });

    let isProcessing = false;
    let currentAudio = null;  // Track currently playing audio

    startBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        if (!topic) return;

        // Show loading state
        startBtn.disabled = true;
        startBtn.textContent = "Generating agents...";

        try {
            const result = await fetch('/start_debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });

            const data = await result.json();

            // Switch panels
            setupPanel.classList.remove('active');
            setupPanel.classList.add('hidden');

            // Wait for animation
            setTimeout(() => {
                setupPanel.style.display = 'none';
                debatePanel.classList.remove('hidden');
                debatePanel.classList.add('active');
            }, 300);

            currentTopicText.textContent = topic;

            // Display generated agents
            displayAgents(data.agents);

            // Auto-trigger first turn
            setTimeout(() => triggerNextTurn(), 500);
        } catch (error) {
            console.error('Error starting debate:', error);
            startBtn.textContent = "Start Simulation";
            startBtn.disabled = false;
        }
    });

    nextTurnBtn.addEventListener('click', () => {
        // If audio is currently playing, skip it
        if (currentAudio && !currentAudio.paused) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
            statusIndicator.classList.add('hidden');
            isProcessing = false;
            nextTurnBtn.textContent = "Next Turn";
            return; // Don't trigger next turn, just stop current audio
        }
        triggerNextTurn();
    });

    async function triggerNextTurn() {
        if (isProcessing) return;
        isProcessing = true;
        statusIndicator.classList.remove('hidden');
        statusIndicator.textContent = "Agent is thinking...";

        try {
            const response = await fetch('/next_turn', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'finished') {
                statusIndicator.textContent = "Debate finished.";
                isProcessing = false;
                return;
            }

            if (data.error) {
                console.error(data.error);
                statusIndicator.textContent = "Error occurred.";
                isProcessing = false;
                return;
            }

            // Add message to UI
            addMessageToChat(data.agent, data.text);

            // Play audio
            if (data.audio_url) {
                statusIndicator.textContent = "Speaking...";
                nextTurnBtn.textContent = "Skip";  // Change button text during playback
                currentAudio = new Audio(data.audio_url);
                currentAudio.onended = () => {
                    statusIndicator.classList.add('hidden');
                    isProcessing = false;
                    nextTurnBtn.textContent = "Next Turn";
                    currentAudio = null;
                };
                currentAudio.play().catch(e => {
                    console.warn("Audio play failed (likely browser policy):", e);
                    isProcessing = false;
                    statusIndicator.classList.add('hidden');
                    nextTurnBtn.textContent = "Next Turn";
                    currentAudio = null;
                });
            } else {
                isProcessing = false;
                statusIndicator.classList.add('hidden');
            }

        } catch (error) {
            console.error('Error fetching turn:', error);
            isProcessing = false;
            statusIndicator.classList.add('hidden');
        }
    }

    function addMessageToChat(agent, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');

        // Determine class based on agent name (simple heuristic)
        if (agent.toLowerCase().includes('lake')) {
            messageDiv.classList.add('lake');
        } else if (agent.toLowerCase().includes('tree')) {
            messageDiv.classList.add('tree');
        } else {
            messageDiv.classList.add('car');
        }

        const nameSpan = document.createElement('span');
        nameSpan.classList.add('agent-name');
        nameSpan.textContent = agent;

        const textNode = document.createTextNode(text);

        messageDiv.appendChild(nameSpan);
        messageDiv.appendChild(textNode);

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function displayAgents(agents) {
        const agentsList = document.getElementById('agents-list');
        const agentsDisplay = document.getElementById('agents-display');

        agentsList.innerHTML = '';

        agents.forEach(agent => {
            const badge = document.createElement('div');
            badge.classList.add('agent-badge');

            const nameSpan = document.createElement('span');
            nameSpan.classList.add('agent-name');
            nameSpan.textContent = agent.name;

            const roleSpan = document.createElement('span');
            roleSpan.classList.add('agent-role');
            roleSpan.textContent = agent.role;

            badge.appendChild(nameSpan);
            badge.appendChild(roleSpan);
            agentsList.appendChild(badge);
        });

        agentsDisplay.classList.remove('hidden');
    }
});
