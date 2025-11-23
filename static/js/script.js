document.addEventListener('DOMContentLoaded', () => {
    const setupPanel = document.getElementById('setup-panel');
    const debatePanel = document.getElementById('debate-panel');
    const startBtn = document.getElementById('start-btn');
    const nextTurnBtn = document.getElementById('next-turn-btn');
    const autoPlayBtn = document.getElementById('auto-play-btn');
    const toggleInputBtn = document.getElementById('toggle-input-btn');
    const modeToggleBtn = document.getElementById('mode-toggle-btn');
    const userInputArea = document.getElementById('user-input-area');
    const userMessageInput = document.getElementById('user-message-input');
    const sendUserMessageBtn = document.getElementById('send-user-message-btn');
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
    let currentAudio = null;
    let audioContext = null;
    let currentDiscussionId = null;
    let agentColorMap = {};  // Map agent names to colors
    let isAutoPlay = false;  // Auto play state
    let isUserInputEnabled = false;  // User input state
    let discussionMode = 'auto';  // Discussion mode: 'auto' or 'round_robin'
    let availableVoices = [];  // Available voices list
    let selectedUserVoice = null;  // User selected voice
    let userClonedVoices = [];  // User cloned voices list

    // Initialize AudioContext
    if (window.AudioContext || window.webkitAudioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    // Load user cloned voices from localStorage
    function loadUserClonedVoices() {
        const stored = localStorage.getItem('userClonedVoices');
        if (stored) {
            try {
                userClonedVoices = JSON.parse(stored);
            } catch (e) {
                userClonedVoices = [];
            }
        }
    }

    // Save user cloned voices to localStorage
    function saveUserClonedVoices() {
        localStorage.setItem('userClonedVoices', JSON.stringify(userClonedVoices));
    }

    // Populate voice selector
    function populateVoiceSelector() {
        const voiceSelector = document.getElementById('voice-selector');
        if (!voiceSelector) return;

        voiceSelector.innerHTML = '';

        // Add preset voices
        availableVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            voiceSelector.appendChild(option);
        });

        // Add separator if there are cloned voices
        if (userClonedVoices.length > 0) {
            const separator = document.createElement('option');
            separator.disabled = true;
            separator.textContent = '───────────────';
            voiceSelector.appendChild(separator);

            // Add user cloned voices
            userClonedVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = `${voice.name} (Cloned)`;
                voiceSelector.appendChild(option);
            });
        }

        // Add "Voice Cloning" option at the end
        const cloningOption = document.createElement('option');
        cloningOption.value = 'clone';
        cloningOption.textContent = '+ Voice Cloning';
        voiceSelector.appendChild(cloningOption);

        // Set default voice (first one or previously selected)
        if (!selectedUserVoice && availableVoices.length > 0) {
            selectedUserVoice = availableVoices[0].id;
        }
        if (selectedUserVoice) {
            voiceSelector.value = selectedUserVoice;
        }
    }

    // Load available voices on page load
    async function loadVoices() {
        try {
            const response = await fetch('/voices');
            const data = await response.json();
            availableVoices = data.voices;

            // Load user cloned voices
            loadUserClonedVoices();

            // Populate voice selector
            populateVoiceSelector();

            // Add change listener
            const voiceSelector = document.getElementById('voice-selector');
            voiceSelector.addEventListener('change', (e) => {
                if (e.target.value === 'clone') {
                    // Show voice cloning modal
                    openVoiceCloningModal();
                } else {
                    selectedUserVoice = e.target.value;
                    console.log('Voice changed to:', selectedUserVoice);
                }
            });

            console.log('Loaded voices:', availableVoices);
            console.log('User cloned voices:', userClonedVoices);
        } catch (error) {
            console.error('Error loading voices:', error);
        }
    }

    // Load voices when page loads
    loadVoices();

    // Auto Play Toggle
    autoPlayBtn.addEventListener('click', () => {
        isAutoPlay = !isAutoPlay;
        autoPlayBtn.classList.toggle('active', isAutoPlay);
        autoPlayBtn.textContent = isAutoPlay ? 'Auto Play: ON' : 'Auto Play: OFF';
    });

    // User Input Toggle
    toggleInputBtn.addEventListener('click', () => {
        isUserInputEnabled = !isUserInputEnabled;
        toggleInputBtn.classList.toggle('active', isUserInputEnabled);
        toggleInputBtn.textContent = isUserInputEnabled ? 'User Input: ON' : 'User Input: OFF';
        userInputArea.classList.toggle('hidden', !isUserInputEnabled);
        if (isUserInputEnabled) {
            userMessageInput.focus();
        }
    });

    // Mode Toggle
    modeToggleBtn.addEventListener('click', async () => {
        if (!currentDiscussionId) return;

        // Toggle mode
        discussionMode = discussionMode === 'auto' ? 'round_robin' : 'auto';
        modeToggleBtn.classList.toggle('active', discussionMode === 'round_robin');
        modeToggleBtn.textContent = discussionMode === 'auto' ? 'Mode: Auto' : 'Mode: Round Robin';

        // Update backend
        try {
            await fetch(`/discussions/${currentDiscussionId}/mode`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: discussionMode })
            });
        } catch (error) {
            console.error('Error updating discussion mode:', error);
        }
    });

    // Send User Message
    async function sendUserMessage() {
        const message = userMessageInput.value.trim();
        if (!message || !currentDiscussionId) return;

        // Stop current audio if playing (same as Skip)
        if (currentAudio) {
            stopCurrentAudio();
        }

        // Clear input
        userMessageInput.value = '';

        // Add user message to chat
        addMessageToChat('You', message);

        // Disable processing to prevent next turn during user TTS
        isProcessing = true;
        statusIndicator.classList.remove('hidden');
        statusIndicator.textContent = "Speaking...";

        // Send to backend with voice_id
        try {
            const response = await fetch(`/discussions/${currentDiscussionId}/user_message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: message,
                    voice_id: selectedUserVoice  // Send user selected voice
                })
            });

            const data = await response.json();

            // Play user's TTS audio if available
            if (data.audio && audioContext) {
                nextTurnBtn.textContent = "Skip";
                await playAudioFromBase64(data.audio, 'You');
                nextTurnBtn.textContent = "Next Turn";
            }

            isProcessing = false;
            statusIndicator.textContent = "Ready";

            // Trigger next turn after user message (with delay)
            setTimeout(() => {
                if (!isProcessing) {
                    triggerNextTurn();
                }
            }, 500);
        } catch (error) {
            console.error('Error sending user message:', error);
            isProcessing = false;
            statusIndicator.textContent = "Error occurred";
        }
    }

    sendUserMessageBtn.addEventListener('click', sendUserMessage);

    // Send on Enter key
    userMessageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });

    startBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        if (!topic) return;

        // Show loading state
        startBtn.disabled = true;
        startBtn.textContent = "Generating agents...";

        try {
            // Create discussion
            const createRes = await fetch('/discussions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });
            const discussion = await createRes.json();
            currentDiscussionId = discussion.id;

            // Initialize discussion (generate roles)
            const initRes = await fetch(`/discussions/${discussion.id}/init`, {
                method: 'POST'
            });
            const data = await initRes.json();

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
            displayAgents(data.roles);

            // Ready for first turn
            startBtn.textContent = "Start Simulation";
            startBtn.disabled = false;

            // Set initial status
            statusIndicator.classList.remove('hidden');
            statusIndicator.textContent = "Ready";

            // Auto start first turn if auto play is enabled
            if (isAutoPlay) {
                setTimeout(() => {
                    triggerNextTurn();
                }, 500);
            }

        } catch (error) {
            console.error('Error starting debate:', error);
            startBtn.textContent = "Start Simulation";
            startBtn.disabled = false;
        }
    });

    nextTurnBtn.addEventListener('click', () => {
        // If audio is currently playing, skip it
        if (currentAudio) {
            stopCurrentAudio();
            return; // Don't trigger next turn, just stop current audio
        }
        triggerNextTurn();
    });

    function stopCurrentAudio() {
        if (currentAudio) {
            try {
                currentAudio.stop();
                currentAudio = null;
            } catch (e) {
                // Already stopped
            }
            statusIndicator.textContent = "Ready";
            isProcessing = false;
            nextTurnBtn.textContent = "Next Turn";
        }
    }

    async function triggerNextTurn() {
        if (isProcessing || !currentDiscussionId) return;
        isProcessing = true;
        statusIndicator.classList.remove('hidden');
        statusIndicator.textContent = "Agent is thinking...";

        try {
            const response = await fetch(`/discussions/${currentDiscussionId}/next_turn`, {
                method: 'POST'
            });
            const data = await response.json();

            if (data.status === 'finished') {
                statusIndicator.textContent = "Debate finished.";
                isProcessing = false;
                nextTurnBtn.disabled = true;
                autoPlayBtn.disabled = true;
                return;
            }

            // Add message to UI
            addMessageToChat(data.agent, data.content);

            // Play audio
            if (data.audio && audioContext) {
                statusIndicator.textContent = "Speaking...";
                nextTurnBtn.textContent = "Skip";  // Change button text during playback
                await playAudioFromBase64(data.audio, data.agent);
                isProcessing = false;
                nextTurnBtn.textContent = "Next Turn";
                currentAudio = null;

                // Auto play next turn if enabled
                if (isAutoPlay) {
                    statusIndicator.textContent = "Ready";
                    setTimeout(() => {
                        triggerNextTurn();
                    }, 500);  // 0.5 seconds delay before auto-playing next turn
                } else {
                    statusIndicator.textContent = "Ready";
                }
            } else {
                isProcessing = false;

                // Auto play next turn if enabled (no audio case)
                if (isAutoPlay) {
                    statusIndicator.textContent = "Ready";
                    setTimeout(() => {
                        triggerNextTurn();
                    }, 500);
                } else {
                    statusIndicator.textContent = "Ready";
                }
            }

        } catch (error) {
            console.error('Error fetching turn:', error);
            isProcessing = false;
            statusIndicator.textContent = "Error occurred";
            setTimeout(() => {
                statusIndicator.textContent = "Ready";
            }, 2000);
        }
    }

    async function playAudioFromBase64(audioBase64, agentName) {
        if (!audioBase64 || !audioContext) {
            return;
        }

        try {
            // Stop previous audio
            stopCurrentAudio();

            // Decode base64 to ArrayBuffer
            const binaryString = atob(audioBase64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }

            // Decode audio data
            const audioBuffer = await audioContext.decodeAudioData(bytes.buffer);

            // Create audio source
            const source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination);
            currentAudio = source;

            // Return Promise
            return new Promise((resolve) => {
                source.onended = () => {
                    console.log(`✅ [${agentName}] Audio playback complete`);
                    currentAudio = null;
                    resolve();
                };

                source.start(0);
                console.log(`🎵 [${agentName}] Started playing audio`);
            });
        } catch (err) {
            console.error('Audio playback failed:', err);
            currentAudio = null;
        }
    }

    function addMessageToChat(agent, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');

        // Determine class based on agent name
        if (agent === 'You') {
            messageDiv.classList.add('user');
        } else {
            const agentClass = getAgentClass(agent);
            messageDiv.classList.add(agentClass);
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

    function getAgentClass(agentName) {
        // Assign colors based on agent order
        if (!agentColorMap[agentName]) {
            const colorClasses = ['lake', 'tree', 'car'];
            const usedColors = Object.values(agentColorMap);
            for (let colorClass of colorClasses) {
                if (!usedColors.includes(colorClass)) {
                    agentColorMap[agentName] = colorClass;
                    break;
                }
            }
            // Fallback
            if (!agentColorMap[agentName]) {
                agentColorMap[agentName] = 'car';
            }
        }
        return agentColorMap[agentName];
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
            roleSpan.textContent = agent.stance || agent.role || '';

            badge.appendChild(nameSpan);
            badge.appendChild(roleSpan);
            agentsList.appendChild(badge);
        });

        agentsDisplay.classList.remove('hidden');
    }

    // Voice Cloning Modal Functions
    const voiceCloningModal = document.getElementById('voice-cloning-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const createVoiceBtn = document.getElementById('create-voice-btn');
    const voiceNameInput = document.getElementById('voice-name-input');
    const voiceDescriptionInput = document.getElementById('voice-description-input');
    const cloningStatus = document.getElementById('cloning-status');
    const recordBtn = document.getElementById('record-btn');
    const recordingTimer = document.getElementById('recording-timer');
    const playbackAudio = document.getElementById('playback-audio');

    let mediaRecorder = null;
    let audioChunks = [];
    let recordingInterval = null;
    let recordingStartTime = 0;
    let recordedBlob = null;

    function openVoiceCloningModal() {
        voiceCloningModal.classList.remove('hidden');
        // Reset form
        voiceNameInput.value = '';
        voiceDescriptionInput.value = '';
        cloningStatus.classList.add('hidden');
        cloningStatus.className = 'status-message hidden';
        recordedBlob = null;
        playbackAudio.classList.add('hidden');
        createVoiceBtn.disabled = true;
        recordBtn.innerHTML = '<span class="record-icon">🎤</span> Start Recording';
        recordBtn.classList.remove('recording');
        recordingTimer.classList.add('hidden');
    }

    function closeVoiceCloningModal() {
        voiceCloningModal.classList.add('hidden');
        // Reset voice selector back to selected voice (not "clone")
        const voiceSelector = document.getElementById('voice-selector');
        if (selectedUserVoice) {
            voiceSelector.value = selectedUserVoice;
        }
    }

    // Recording functionality
    recordBtn.addEventListener('click', async () => {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    recordedBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(recordedBlob);
                    playbackAudio.src = audioUrl;
                    playbackAudio.classList.remove('hidden');
                    createVoiceBtn.disabled = false;

                    // Stop all tracks
                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start();
                recordingStartTime = Date.now();
                recordBtn.innerHTML = '<span class="record-icon">⏹️</span> Stop Recording';
                recordBtn.classList.add('recording');
                recordingTimer.classList.remove('hidden');

                // Update timer
                recordingInterval = setInterval(() => {
                    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    recordingTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }, 1000);

            } catch (error) {
                console.error('Error accessing microphone:', error);
                showCloningStatus('Error accessing microphone. Please allow microphone access.', 'error');
            }
        } else {
            // Stop recording
            mediaRecorder.stop();
            recordBtn.innerHTML = '<span class="record-icon">🎤</span> Start Recording';
            recordBtn.classList.remove('recording');
            clearInterval(recordingInterval);
        }
    });

    closeModalBtn.addEventListener('click', closeVoiceCloningModal);

    // Close modal when clicking outside
    voiceCloningModal.addEventListener('click', (e) => {
        if (e.target === voiceCloningModal) {
            closeVoiceCloningModal();
        }
    });

    // Create Voice Clone
    createVoiceBtn.addEventListener('click', async () => {
        const voiceName = voiceNameInput.value.trim();

        if (!voiceName) {
            showCloningStatus('Please enter a voice name', 'error');
            return;
        }

        if (!recordedBlob) {
            showCloningStatus('Please record your voice first', 'error');
            return;
        }

        // Disable button and show loading
        createVoiceBtn.disabled = true;
        createVoiceBtn.textContent = 'Creating...';
        showCloningStatus('Creating your voice clone...', 'loading');

        try {
            // Create FormData with recorded audio
            const formData = new FormData();
            formData.append('name', voiceName);

            // Convert Blob to File with proper name and type
            const audioFile = new File([recordedBlob], `${voiceName}.wav`, { type: 'audio/wav' });
            formData.append('audio', audioFile);

            const description = voiceDescriptionInput.value.trim();
            if (description) {
                formData.append('description', description);
            }

            // Send to backend
            const response = await fetch('/clone_voice', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.voice_id) {
                // Success - add to user cloned voices
                const newVoice = {
                    id: data.voice_id,
                    name: voiceName,
                    description: description
                };
                userClonedVoices.push(newVoice);
                saveUserClonedVoices();

                // Update voice selector
                populateVoiceSelector();

                // Set as selected voice
                selectedUserVoice = data.voice_id;
                const voiceSelector = document.getElementById('voice-selector');
                voiceSelector.value = selectedUserVoice;

                showCloningStatus('Voice clone created successfully!', 'success');

                // Close modal after 1.5 seconds
                setTimeout(() => {
                    closeVoiceCloningModal();
                }, 1500);
            } else {
                showCloningStatus(data.error || 'Failed to create voice clone', 'error');
            }
        } catch (error) {
            console.error('Error creating voice clone:', error);
            showCloningStatus('Error creating voice clone. Please try again.', 'error');
        } finally {
            createVoiceBtn.disabled = false;
            createVoiceBtn.textContent = 'Create Voice Clone';
        }
    });

    function showCloningStatus(message, type) {
        cloningStatus.textContent = message;
        cloningStatus.className = `status-message ${type}`;
        cloningStatus.classList.remove('hidden');
    }
});
