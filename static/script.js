document.addEventListener('DOMContentLoaded', () => {
    const setupPanel = document.getElementById('setup-panel');
    const debatePanel = document.getElementById('debate-panel');
    const startBtn = document.getElementById('start-btn');
    const nextTurnBtn = document.getElementById('next-turn-btn');
    const topicInput = document.getElementById('topic-input');
    const currentTopicText = document.getElementById('current-topic-text');
    const chatContainer = document.getElementById('chat-container');
    const statusIndicator = document.getElementById('status-indicator');

    let isProcessing = false;

    startBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        if (!topic) return;

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

        try {
            await fetch('/start_debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });
            
            // Auto-trigger first turn
            triggerNextTurn();
        } catch (error) {
            console.error('Error starting debate:', error);
        }
    });

    nextTurnBtn.addEventListener('click', triggerNextTurn);

    async function triggerNextTurn() {
        if (isProcessing) return;
        isProcessing = true;
        nextTurnBtn.disabled = true;
        statusIndicator.classList.remove('hidden');
        statusIndicator.textContent = "Agent is thinking...";

        try {
            const response = await fetch('/next_turn', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'finished') {
                statusIndicator.textContent = "Debate finished.";
                return;
            }

            if (data.error) {
                console.error(data.error);
                statusIndicator.textContent = "Error occurred.";
                return;
            }

            // Add message to UI
            addMessageToChat(data.agent, data.text);

            // Play audio
            if (data.audio_url) {
                statusIndicator.textContent = "Speaking...";
                const audio = new Audio(data.audio_url);
                audio.onended = () => {
                    statusIndicator.classList.add('hidden');
                    isProcessing = false;
                    nextTurnBtn.disabled = false;
                };
                audio.play().catch(e => {
                    console.warn("Audio play failed (likely browser policy):", e);
                    isProcessing = false;
                    nextTurnBtn.disabled = false;
                    statusIndicator.classList.add('hidden');
                });
            } else {
                isProcessing = false;
                nextTurnBtn.disabled = false;
                statusIndicator.classList.add('hidden');
            }

        } catch (error) {
            console.error('Error fetching turn:', error);
            isProcessing = false;
            nextTurnBtn.disabled = false;
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
});
