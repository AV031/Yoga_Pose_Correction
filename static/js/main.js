/* ============================================
   YOGA POSE ESTIMATOR - Main JavaScript
   ============================================ */

// Global variables
window.currentSessionId = null;
let currentSessionId = null;
let sessionStartTime = null;
let poses = [];

window.socket = io(window.location.origin, {
    transports: ['websocket', 'polling'],
    path: '/socket.io',
    autoConnect: true,
    timeout: 20000,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 500,
    timeout: 20000
});
const socket = window.socket;

// DOM Elements
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.section');
const connectionStatus = document.querySelector('.connection-status');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('.status-text');
const posesGrid = document.getElementById('posesGrid');

/* ========================
   INITIALIZATION
   ======================== */
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    loadPoses();
    setupSocketListeners();
});

/* ========================
   NAVIGATION
   ======================== */
function initializeNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('data-section');
            navigateToSection(sectionId);
        });
    });
}

function navigateToSection(sectionId) {
    // Update active nav link
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === sectionId) {
            link.classList.add('active');
        }
    });
    
    // Update active section
    sections.forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
    
    // Load history if needed
    if (sectionId === 'history') {
        loadSessionHistory();
    }
}

function navigateToSession() {
    navigateToSection('session');
}

/* ========================
   SOCKET.IO LISTENERS
   ======================== */
function setupSocketListeners() {
    socket.on('connect', () => {
        updateConnectionStatus(true);
        console.log('Connected to server');
        showNotification('Connected to server', 'success');
    });

    socket.on('connect_timeout', () => {
        updateConnectionStatus(false);
        console.error('Socket connect_timeout');
        showNotification('Socket timeout connecting to server', 'error');
    });

    socket.on('disconnect', (reason) => {
        updateConnectionStatus(false);
        console.log('Disconnected from server:', reason);
        showNotification('Disconnected from server: ' + reason, 'warning');
        console.error('Socket connect_error:', error);
        showNotification('Socket connect error: ' + (error.message || error), 'error');
    });

    socket.on('response', (data) => {
        console.log('Server response:', data);
    });

    socket.on('error', (data) => {
        updateConnectionStatus(false);
        console.error('Socket error:', data);
        const msg = data && data.message ? data.message : JSON.stringify(data);
        showNotification('Server error: ' + msg, 'error');
    });
    
    socket.on('pose_detected', handlePoseDetected);
    socket.on('detection_started', handleDetectionStarted);
    socket.on('no_person_detected', handleNoPersonDetected);
}

function updateConnectionStatus(connected) {
    connectionStatus.classList.toggle('connected', connected);
    statusIndicator.style.background = connected ? '#00D084' : '#FF4757';
    statusText.textContent = connected ? 'Connected' : 'Disconnected';
}

/* ========================
   POSES MANAGEMENT
   ======================== */
async function loadPoses() {
    try {
        const response = await fetch('/api/poses');
        poses = await response.json();
        displayPoses();
    } catch (error) {
        console.error('Error loading poses:', error);
    }
}

function displayPoses() {
    if (!posesGrid) return;
    
    posesGrid.innerHTML = poses.map(pose => `
        <div class="pose-card">
            <div class="icon">${getPoseIcon(pose.name)}</div>
            <div class="name">${pose.name}</div>
            <div class="level">${pose.difficulty}</div>
        </div>
    `).join('');
}

function getPoseIcon(poseName) {
    const iconMap = {
        'Mountain Pose': '🧘',
        'Warrior I': '⚔️',
        'Warrior II': '⚔️',
        'Tree Pose': '🌳',
        'Downward Dog': '🐶',
        'Child Pose': '🤲',
        'Cobra Pose': '🐍',
        'Triangle Pose': '△',
        'Plank Pose': '━',
        'Bridge Pose': '🌉'
    };
    return iconMap[poseName] || '🧘';
}

/* ========================
   SESSION HISTORY
   ======================== */
async function loadSessionHistory() {
    const historyList = document.getElementById('historyList');
    
    try {
        historyList.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i><p>Loading sessions...</p></div>';
        
        const response = await fetch('/api/sessions');
        const sessions = await response.json();
        
        if (sessions.length === 0) {
            historyList.innerHTML = '<p class="placeholder">No sessions found. Start your first yoga session!</p>';
            return;
        }
        
        historyList.innerHTML = sessions.map(session => `
            <div class="history-item">
                <div class="history-item-header">
                    <div class="history-item-title">
                        <i class="fas fa-video"></i> Session ${session.session_id.split('_')[1]}
                    </div>
                    <div class="history-item-date">${formatDate(session.start_time)}</div>
                </div>
                <div class="history-item-stats">
                    <div class="stat">
                        <span class="stat-label">Duration</span>
                        <span class="stat-value">${session.duration}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Frames</span>
                        <span class="stat-value">${session.total_frames}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Unique Poses</span>
                        <span class="stat-value">${session.poses_detected}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Avg Accuracy</span>
                        <span class="stat-value">${(session.average_accuracy * 100).toFixed(1)}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Best Accuracy</span>
                        <span class="stat-value">${(session.highest_accuracy * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading session history:', error);
        historyList.innerHTML = '<p class="placeholder">Error loading sessions</p>';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
}

/* ========================
   POSE DETECTION HANDLERS
   ======================== */
function handlePoseDetected(data) {
    // Update pose name
    document.getElementById('detectedPose').textContent = data.pose || 'Unknown';
    
    // Update confidence
    const confidence = (data.confidence * 100).toFixed(1);
    document.getElementById('confidenceText').textContent = `${confidence}%`;
    document.getElementById('confidenceFill').style.width = `${confidence}%`;
    
    // Update accuracy
    const accuracy = (data.accuracy * 100).toFixed(1);
    document.getElementById('accuracyPercent').textContent = accuracy;
    updateAccuracyCircle(parseFloat(accuracy));
    
    // Update metrics
    if (data.stats) {
        document.getElementById('shoulderAngle').textContent = 
            data.stats.shoulder_angle ? data.stats.shoulder_angle.toFixed(1) : '—';
        document.getElementById('elbowAngle').textContent = 
            data.stats.elbow_angle ? data.stats.elbow_angle.toFixed(1) : '—';
        document.getElementById('kneeAngle').textContent = 
            data.stats.knee_angle ? data.stats.knee_angle.toFixed(1) : '—';
        document.getElementById('stability').textContent = 
            data.stats.stability ? data.stats.stability.toFixed(1) : '—';
    }
    
    // Update frame
    if (data.frame) {
        const canvas = document.getElementById('detectionCanvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        };
        img.src = data.frame;
    }
    
    // Update feedback
    if (data.feedback && data.feedback.length > 0) {
        updateFeedback(data.feedback);
    }
}

function handleDetectionStarted(data) {
    console.log('Detection started for session:', data.session_id);
    document.getElementById('sessionStatus').textContent = 'Detecting';
}

function handleNoPersonDetected(data) {
    document.getElementById('detectedPose').textContent = 'No Person Detected';
    document.getElementById('feedbackList').innerHTML = 
        '<p class="placeholder">Position yourself in front of the camera</p>';
}

function updateAccuracyCircle(accuracy) {
    const circle = document.getElementById('accuracyCircle');
    if (circle) {
        const circumference = 282.7;
        const offset = circumference - (accuracy / 100) * circumference;
        circle.style.strokeDashoffset = offset;
    }
}

function updateFeedback(feedbackList) {
    const feedbackPanel = document.getElementById('feedbackList');
    feedbackPanel.innerHTML = feedbackList.map((item, index) => `
        <div class="feedback-item ${item.type || ''}">
            <strong>${item.title}:</strong> ${item.message}
        </div>
    `).join('');
}

/* ========================
   NOTIFICATIONS
   ======================== */
function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with a proper notification library)
    console.log(`[${type.toUpperCase()}] ${message}`);
}

/* ========================
   UTILITY FUNCTIONS
   ======================== */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    const parts = [];
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    parts.push(`${secs}s`);
    
    return parts.join(' ');
}

function generateGradient(ctx, x0, y0, x1, y1) {
    const gradient = ctx.createLinearGradient(x0, y0, x1, y1);
    gradient.addColorStop(0, '#FF6B6B');
    gradient.addColorStop(1, '#4ECDC4');
    return gradient;
}

// Export functions for use in session.js
window.navigateToSession = navigateToSession;
window.navigateToSection = navigateToSection;
window.showNotification = showNotification;
