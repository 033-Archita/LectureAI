"""
Audio recording utilities for live recording feature
This provides browser-based audio recording capabilities
"""

def get_audio_recorder_html() -> str:
    """
    Returns HTML/JavaScript code for browser-based audio recording
    
    Returns:
        HTML string with audio recording functionality
    """
    return """
    <div id="audio-recorder" style="font-family: 'Inter', sans-serif;">
        <style>
            .recorder-container {
                background: white;
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08);
                text-align: center;
            }
            
            .record-button {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                border: none;
                background: linear-gradient(135deg, #FF6B6B 0%, #E57373 100%);
                color: white;
                font-size: 2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(229, 115, 115, 0.3);
                margin: 1rem auto;
            }
            
            .record-button:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(229, 115, 115, 0.4);
            }
            
            .record-button.recording {
                background: #E53935;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            .record-button.stopped {
                background: #666;
            }
            
            .timer {
                font-size: 1.5rem;
                font-weight: 600;
                color: #333;
                margin: 1rem 0;
            }
            
            .status {
                font-size: 1rem;
                color: #666;
                margin: 0.5rem 0;
            }
            
            .waveform {
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 3px;
                margin: 1rem 0;
            }
            
            .bar {
                width: 4px;
                background: #E57373;
                border-radius: 2px;
                transition: height 0.1s ease;
            }
        </style>
        
        <div class="recorder-container">
            <h3 style="color: #1a1a1a; margin-bottom: 1rem;">🎙️ Live Audio Recording</h3>
            <p class="status" id="status">Click the button to start recording</p>
            
            <button class="record-button" id="recordButton" onclick="toggleRecording()">
                <span id="buttonIcon">●</span>
            </button>
            
            <div class="timer" id="timer">00:00</div>
            
            <div class="waveform" id="waveform">
                <div class="bar" style="height: 10px;"></div>
                <div class="bar" style="height: 20px;"></div>
                <div class="bar" style="height: 15px;"></div>
                <div class="bar" style="height: 25px;"></div>
                <div class="bar" style="height: 18px;"></div>
                <div class="bar" style="height: 30px;"></div>
                <div class="bar" style="height: 22px;"></div>
                <div class="bar" style="height: 12px;"></div>
            </div>
            
            <p style="font-size: 0.9rem; color: #999; margin-top: 1rem;">
                💡 Tip: Speak clearly and minimize background noise
            </p>
        </div>
        
        <script>
            let mediaRecorder;
            let audioChunks = [];
            let startTime;
            let timerInterval;
            let audioContext;
            let analyser;
            let dataArray;
            let animationId;
            
            async function toggleRecording() {
                const button = document.getElementById('recordButton');
                const icon = document.getElementById('buttonIcon');
                const status = document.getElementById('status');
                
                if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        
                        // Setup audio analysis for waveform
                        audioContext = new AudioContext();
                        const source = audioContext.createMediaStreamSource(stream);
                        analyser = audioContext.createAnalyser();
                        analyser.fftSize = 256;
                        const bufferLength = analyser.frequencyBinCount;
                        dataArray = new Uint8Array(bufferLength);
                        source.connect(analyser);
                        
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        
                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };
                        
                        mediaRecorder.onstop = () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            
                            // Create download link
                            const a = document.createElement('a');
                            a.href = audioUrl;
                            a.download = 'recording_' + Date.now() + '.wav';
                            a.click();
                            
                            status.textContent = 'Recording saved! You can now upload it.';
                            stopWaveformAnimation();
                        };
                        
                        mediaRecorder.start();
                        startTime = Date.now();
                        startTimer();
                        startWaveformAnimation();
                        
                        button.classList.add('recording');
                        button.classList.remove('stopped');
                        icon.textContent = '■';
                        status.textContent = 'Recording in progress...';
                        
                    } catch (err) {
                        status.textContent = 'Error: Could not access microphone. Please allow microphone access.';
                        console.error('Error accessing microphone:', err);
                    }
                } else if (mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    clearInterval(timerInterval);
                    
                    button.classList.remove('recording');
                    button.classList.add('stopped');
                    icon.textContent = '●';
                    
                    if (audioContext) {
                        audioContext.close();
                    }
                }
            }
            
            function startTimer() {
                timerInterval = setInterval(() => {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    document.getElementById('timer').textContent = 
                        String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
                }, 1000);
            }
            
            function startWaveformAnimation() {
                const bars = document.querySelectorAll('.bar');
                
                function animate() {
                    if (analyser) {
                        analyser.getByteFrequencyData(dataArray);
                        
                        bars.forEach((bar, i) => {
                            const index = Math.floor(i * dataArray.length / bars.length);
                            const value = dataArray[index];
                            const height = Math.max(10, (value / 255) * 40);
                            bar.style.height = height + 'px';
                        });
                    }
                    
                    animationId = requestAnimationFrame(animate);
                }
                
                animate();
            }
            
            function stopWaveformAnimation() {
                if (animationId) {
                    cancelAnimationFrame(animationId);
                }
                const bars = document.querySelectorAll('.bar');
                bars.forEach(bar => {
                    bar.style.height = '10px';
                });
            }
        </script>
    </div>
    """

def get_recording_instructions() -> str:
    """
    Returns instructions for using the live recording feature
    
    Returns:
        Markdown formatted instructions
    """
    return """
    ### 🎙️ How to Use Live Recording
    
    1. **Click the red button** to start recording
    2. **Speak your lecture** - the timer will show duration
    3. **Click the square button** to stop recording
    4. **File will auto-download** - then upload it back to LectureAI
    5. **Generate notes** from your recording!
    
    **Tips for Best Results:**
    - Use a quiet environment
    - Speak clearly and at a moderate pace
    - Keep microphone 6-12 inches from your mouth
    - Avoid background music or noise
    - Test your microphone first with a short recording
    
    **Recommended For:**
    - Live lectures you're giving
    - Voice notes during study sessions
    - Recording discussions or presentations
    - Creating audio for later transcription
    """
