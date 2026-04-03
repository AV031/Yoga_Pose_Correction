/* ============================================
   YOGA POSE ESTIMATOR - Session JavaScript
   ============================================ */

let videoStream = null;
let isCapturing = false;
let sessionInterval = null;

const videoFeed = document.getElementById('videoFeed');
const detectionCanvas = document.getElementById('detectionCanvas');
const startCaptureBtn = document.getElementById('startCaptureBtn');
const stopCaptureBtn = document.getElementById('stopCaptureBtn');
const endSessionBtn = document.getElementById('endSessionBtn');
const saveSessionBtn = document.getElementById('saveSessionBtn');
const sessionIdDisplay = document.getElementById('sessionIdDisplay');
const sessionStatus = document.getElementById('sessionStatus');
const sessionDuration = document.getElementById('sessionDuration');

/* ========================
   SESSION INITIALIZATION
   ======================== */
document.addEventListener('DOMContentLoaded', () => {
    setupSessionListeners();
});

function setupSessionListeners() {
    if (startCaptureBtn) {
        startCaptureBtn.addEventListener('click', startSession);
    }
    if (stopCaptureBtn) {
        stopCaptureBtn.addEventListener('click', stopSession);
    }
    if (endSessionBtn) {
        endSessionBtn.addEventListener('click', endSession);
    }
    if (saveSessionBtn) {
        saveSessionBtn.addEventListener('click', saveSession);
    }
}

/* ========================
   SESSION MANAGEMENT
   ======================== */
async function startSession() {
    try {
        // Request camera access
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'user',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        });
        
        videoFeed.srcObject = videoStream;
        
        // Start server session
        const response = await fetch('/api/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        window.currentSessionId = data.session_id;
        
        // Update UI
        sessionIdDisplay.textContent = data.session_id;
        sessionStatus.textContent = 'Active';
        startCaptureBtn.style.display = 'none';
        stopCaptureBtn.style.display = 'inline-flex';
        saveSessionBtn.disabled = false;
        isCapturing = true;
        
        // Start tracking duration
        const startTime = Date.now();
        sessionInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const mins = Math.floor(elapsed / 60);
            const secs = elapsed % 60;
            sessionDuration.textContent = 
                `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }, 1000);
        
        // Start frame processing
        startFrameCapture();
        
        showNotification('Session started', 'success');
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        showNotification('Camera access denied', 'error');
    }
}

async function stopSession() {
    isCapturing = false;
    
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    
    if (sessionInterval) {
        clearInterval(sessionInterval);
    }
    
    startCaptureBtn.style.display = 'inline-flex';
    stopCaptureBtn.style.display = 'none';
    sessionStatus.textContent = 'Paused';
    
    showNotification('Session paused', 'info');
}

async function endSession() {
    if (!window.currentSessionId) {
        showNotification('No active session', 'warning');
        return;
    }
    
    try {
        await stopSession();
        
        const response = await fetch(`/api/session/${window.currentSessionId}/end`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // Reset UI
        sessionIdDisplay.textContent = '—';
        sessionStatus.textContent = 'Ready';
        sessionDuration.textContent = '00:00';
        document.getElementById('detectedPose').textContent = 'Waiting...';
        document.getElementById('confidenceFill').style.width = '0%';
        document.getElementById('confidenceText').textContent = '0%';
        document.getElementById('accuracyPercent').textContent = '0';
        document.getElementById('feedbackList').innerHTML = 
            '<p class="placeholder">Hold a pose for real-time feedback</p>';
        
        window.currentSessionId = null;
        
        // Show summary
        showSessionSummary(data.summary);
        showNotification('Session ended and saved', 'success');
        
    } catch (error) {
        console.error('Error ending session:', error);
        showNotification('Error ending session', 'error');
    }
}

async function saveSession() {
    if (!window.currentSessionId) {
        showNotification('No active session to save', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/session/${window.currentSessionId}/summary`);
        const summary = await response.json();
        
        // Download as JSON
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/json;charset=utf-8,' + 
            encodeURIComponent(JSON.stringify(summary, null, 2)));
        element.setAttribute('download', `yoga_session_${window.currentSessionId}.json`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        showNotification('Session saved', 'success');
        
    } catch (error) {
        console.error('Error saving session:', error);
        showNotification('Error saving session', 'error');
    }
}

function showSessionSummary(summary) {
    const summaryHtml = `
        <div style="background: rgba(0, 208, 132, 0.2); border: 1px solid rgba(0, 208, 132, 0.5); 
                    border-radius: 12px; padding: 1.5rem; margin-top: 2rem; color: #fff;">
            <h3 style="color: #00D084; margin-bottom: 1rem;">Session Summary</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <div>
                    <span style="color: #B8B8D1;">Duration:</span>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #00D084;">${summary.duration}</div>
                </div>
                <div>
                    <span style="color: #B8B8D1;">Total Frames:</span>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #00D084;">${summary.total_frames}</div>
                </div>
                <div>
                    <span style="color: #B8B8D1;">Poses Detected:</span>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #00D084;">${summary.poses_detected}</div>
                </div>
                <div>
                    <span style="color: #B8B8D1;">Avg Accuracy:</span>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #00D084;">
                        ${(summary.average_accuracy * 100).toFixed(1)}%
                    </div>
                </div>
                <div>
                    <span style="color: #B8B8D1;">Best Accuracy:</span>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #00D084;">
                        ${(summary.highest_accuracy * 100).toFixed(1)}%
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Insert after session footer
    const footer = document.querySelector('.session-footer');
    const existingSummary = document.querySelector('[data-summary]');
    if (existingSummary) existingSummary.remove();
    
    const summaryDiv = document.createElement('div');
    summaryDiv.setAttribute('data-summary', 'true');
    summaryDiv.innerHTML = summaryHtml;
    footer.parentNode.insertBefore(summaryDiv, footer.nextSibling);
}

/* ========================
   FRAME CAPTURE & PROCESSING
   ======================== */
function startFrameCapture() {
    const ctx = detectionCanvas.getContext('2d');
    
    function captureFrame() {
        if (!isCapturing || !videoStream) return;
        
        // Set canvas size to match video
        if (videoFeed.videoWidth > 0) {
            detectionCanvas.width = videoFeed.videoWidth;
            detectionCanvas.height = videoFeed.videoHeight;
            
            // Draw video frame
            ctx.drawImage(videoFeed, 0, 0);
            
            // Convert to base64
            const imageData = detectionCanvas.toDataURL('image/jpeg', 0.8);
            
            // Send to server
            if (window.socket && window.currentSessionId) {
                window.socket.emit('process_frame', {
                    session_id: window.currentSessionId,
                    image: imageData
                });
            }
        }
        
        // Continue capturing at ~30 FPS
        setTimeout(captureFrame, 33);
    }
    
    captureFrame();
}

/* ========================
   POSE ANALYSIS HELPERS
   ======================== */
function calculateAngle(p1, p2, p3) {
    /**
     * Calculate angle between three points
     * p1, p2, p3: {x, y} objects
     */
    const angle1 = Math.atan2(p1.y - p2.y, p1.x - p2.x);
    const angle2 = Math.atan2(p3.y - p2.y, p3.x - p2.x);
    const angle = Math.abs(angle1 - angle2);
    
    return (angle * 180 / Math.PI);
}

function getDistance(p1, p2) {
    /**
     * Calculate distance between two points
     */
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
}

/* ========================
   UTILITY FUNCTIONS
   ======================== */
function drawPose(landmarks, ctx, canvas) {
    /**
     * Draw pose skeleton on canvas
     */
    if (!landmarks || !ctx) return;
    
    const connections = [
        // Head
        [0, 1], [1, 2], [2, 3], [3, 7],
        [0, 4], [4, 5], [5, 6], [6, 8],
        
        // Torso
        [9, 10],
        [11, 12],
        [11, 13], [13, 15],
        [12, 14], [14, 16],
        
        // Legs
        [11, 23],
        [12, 24],
        [23, 25], [25, 27],
        [24, 26], [26, 28],
        [27, 29], [28, 30],
        [29, 31], [30, 32]
    ];
    
    // Draw connections
    ctx.strokeStyle = '#4ECDC4';
    ctx.lineWidth = 2;
    connections.forEach(([start, end]) => {
        if (landmarks[start] && landmarks[end]) {
            ctx.beginPath();
            ctx.moveTo(landmarks[start].x * canvas.width, landmarks[start].y * canvas.height);
            ctx.lineTo(landmarks[end].x * canvas.width, landmarks[end].y * canvas.height);
            ctx.stroke();
        }
    });
    
    // Draw landmarks
    ctx.fillStyle = '#FF6B6B';
    landmarks.forEach(landmark => {
        if (landmark) {
            ctx.beginPath();
            ctx.arc(landmark.x * canvas.width, landmark.y * canvas.height, 4, 0, 2 * Math.PI);
            ctx.fill();
        }
    });
}

// Export for use in main.js
window.calculateAngle = calculateAngle;
window.getDistance = getDistance;
window.drawPose = drawPose;
