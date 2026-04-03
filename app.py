#!/usr/bin/env python3
"""
Yoga Pose Estimator Web Application
Flask backend for professional web UI
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import json
import base64
import os
from datetime import datetime
import threading
from queue import Queue

from pose_detector import PoseDetector
from pose_analyzer import PoseAnalyzer
from reference_poses import ReferencePoses

# Import LSTM model separately - will be lazy loaded
try:
    from lstm_model import YogaPoseLSTM
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    YogaPoseLSTM = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoga_pose_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
pose_detector = PoseDetector()
pose_analyzer = PoseAnalyzer()
reference_poses = ReferencePoses()
lstm_model = None

if LSTM_AVAILABLE:
    try:
        lstm_model = YogaPoseLSTM()
        lstm_model.load_model('yoga_pose_lstm.h5')
    except Exception as e:
        print(f"Warning: Could not load LSTM model: {e}")
        lstm_model = None

# Session management
active_sessions = {}
session_data_dir = 'session_data'
os.makedirs(session_data_dir, exist_ok=True)

# Camera thread management
camera_threads = {}
camera_queues = {}
landmarks_buffers = {}  # Buffer for LSTM sequence


class PoseSessionTracker:
    """Track pose data for a session"""
    def __init__(self, session_id):
        self.session_id = session_id
        self.start_time = datetime.now()
        self.poses_detected = []
        self.current_pose = None
        self.accuracy_history = []
        self.total_frames = 0
        self.highest_accuracy = 0
        
    def add_pose_data(self, pose_name, accuracy, landmarks):
        self.poses_detected.append({
            'pose': pose_name,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat(),
            'landmarks': landmarks
        })
        self.accuracy_history.append(accuracy)
        self.total_frames += 1
        self.highest_accuracy = max(self.highest_accuracy, accuracy)
        
    def get_summary(self):
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'duration': str(datetime.now() - self.start_time),
            'total_frames': self.total_frames,
            'poses_detected': len(set([p['pose'] for p in self.poses_detected])),
            'average_accuracy': np.mean(self.accuracy_history) if self.accuracy_history else 0,
            'highest_accuracy': self.highest_accuracy
        }


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/poses')
def get_poses():
    """Get list of supported poses"""
    poses = reference_poses.get_poses_list()
    return jsonify(poses)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new pose estimation session"""
    data = request.json
    session_id = f"session_{int(datetime.now().timestamp())}"
    tracker = PoseSessionTracker(session_id)
    active_sessions[session_id] = tracker
    
    return jsonify({
        'session_id': session_id,
        'status': 'started',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/session/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """End a pose estimation session and save data"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    tracker = active_sessions[session_id]
    summary = tracker.get_summary()
    
    # Save session data
    session_file = os.path.join(session_data_dir, f"{session_id}.json")
    with open(session_file, 'w') as f:
        json.dump({
            'summary': summary,
            'data': tracker.poses_detected
        }, f, indent=2)
    
    # Clean up buffers
    if session_id in landmarks_buffers:
        del landmarks_buffers[session_id]
    
    del active_sessions[session_id]
    
    return jsonify({
        'status': 'ended',
        'summary': summary
    })


@app.route('/api/session/<session_id>/summary', methods=['GET'])
def get_session_summary(session_id):
    """Get session summary"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    tracker = active_sessions[session_id]
    return jsonify(tracker.get_summary())


@app.route('/api/sessions', methods=['GET'])
def get_all_sessions():
    """Get all saved sessions"""
    sessions = []
    for file in os.listdir(session_data_dir):
        if file.endswith('.json'):
            with open(os.path.join(session_data_dir, file), 'r') as f:
                data = json.load(f)
                sessions.append(data['summary'])
    
    return jsonify(sorted(sessions, key=lambda x: x['start_time'], reverse=True))


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('response', {'data': 'Connected to Yoga Pose Estimator'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('start_pose_detection')
def start_pose_detection(data):
    """Start real-time pose detection"""
    session_id = data.get('session_id')
    pose_target = data.get('target_pose', 'All')
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Invalid session'})
        return
    
    emit('detection_started', {'session_id': session_id})


@socketio.on('process_frame')
def process_frame(data):
    """Process a frame from the client"""
    try:
        session_id = data.get('session_id')
        image_data = data.get('image')
        
        if not session_id or session_id not in active_sessions:
            emit('error', {'message': 'Invalid session'})
            return
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect pose
        landmarks, frame_with_pose = pose_detector.detect_pose(frame)

        if landmarks is None:
            print(f"[Pose] No landmarks detected for session {session_id}")
            emit('no_person_detected', {'message': 'No person detected in frame'})
            return

        # Build detectable angles for analysis
        detected_angles = pose_detector.get_key_angles(landmarks)
        analysis = pose_analyzer.analyze_pose(detected_angles)

        # Add to buffer for LSTM
        if session_id not in landmarks_buffers:
            landmarks_buffers[session_id] = []

        landmarks_buffers[session_id].append(landmarks)
        if len(landmarks_buffers[session_id]) > 60:  # Keep last 60 frames
            landmarks_buffers[session_id].pop(0)

        # Classify with LSTM (using realtime prediction)
        if lstm_model:
            detected_pose_name, confidence = lstm_model.predict_realtime(landmarks_buffers[session_id])
        else:
            detected_pose_name = None
            confidence = 0.0

        # If LSTM is not available, use pose analyzer motif
        analyzer_pose_key = analysis.get('reference_match')
        pose_name = detected_pose_name or analyzer_pose_key or 'unknown'

        if pose_name and pose_name != 'unknown':
            pose_info = reference_poses.get_pose_info(pose_name)
            pose_label = pose_info.get('name', pose_name)
        else:
            pose_label = 'Unknown Pose'

        # Get accuracy (prefer analyzer score)
        accuracy = float(analysis.get('accuracy_score', 0.0))
        confidence = float(confidence if confidence is not None else accuracy)

        # Track session data
        tracker = active_sessions[session_id]
        tracker.add_pose_data(pose_name, accuracy, landmarks.tolist())

        # Encode response frame to send back to client
        _, buffer = cv2.imencode('.jpg', frame_with_pose)
        img_str = base64.b64encode(buffer).decode()

        emit('pose_detected', {
            'pose': pose_label,
            'pose_key': pose_name,
            'confidence': float(confidence),
            'accuracy': float(accuracy),
            'frame': f'data:image/jpeg;base64,{img_str}',
            'feedback': analysis.get('feedback', []),
            'stats': {
                'shoulder_angle': analysis.get('shoulder_angle'),
                'elbow_angle': analysis.get('elbow_angle'),
                'knee_angle': analysis.get('knee_angle'),
                'stability': analysis.get('stability_score')
            }
        })

    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        emit('error', {'message': str(e)})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'pose_detector': 'ready',
            'lstm_model': 'ready',
            'reference_poses': 'ready'
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    YOGA POSE ESTIMATOR - WEB APPLICATION                     ║
    ║                                                              ║
    ║    Starting Flask server...                                  ║
    ║    Open http://localhost:5000 in your browser               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run with SocketIO support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
