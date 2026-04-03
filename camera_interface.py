import cv2
import numpy as np
import os
import time
from typing import Optional, Callable, Dict, List, Tuple
from pose_detector import PoseDetector
from lstm_model import YogaPoseLSTM
from pose_analyzer import PoseAnalyzer
import threading

class CameraInterface:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
        self.pose_detector = PoseDetector()
        self.pose_analyzer = PoseAnalyzer()
        self.lstm_model = None
        
        # Buffer for sequence data
        self.landmarks_buffer = []
        self.sequence_length = 30
        
        # UI elements
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.thickness = 2
        
        # Colors
        self.colors = {
            'text': (255, 255, 255),
            'background': (0, 0, 0),
            'good': (0, 255, 0),
            'warning': (0, 255, 255),
            'error': (0, 0, 255),
            'skeleton': (0, 255, 0),
            'highlight': (255, 0, 255)
        }
        
        # Session data
        self.session_data = []
        self.current_pose = None
        self.previous_pose = None
        self.stability_score = 0.0
        
    def initialize_camera(self) -> bool:
        """Initialize camera capture"""
        self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            print(f"Warning: Could not open camera {self.camera_id}. Trying fallback camera ids...")
            for candidate_id in range(0, 5):
                if candidate_id == self.camera_id:
                    continue
                temp_cap = cv2.VideoCapture(candidate_id)
                if temp_cap.isOpened():
                    print(f"✅ Fallback camera found: {candidate_id}")
                    self.camera_id = candidate_id
                    self.cap = temp_cap
                    break
                temp_cap.release()

        if not self.cap.isOpened():
            print("Error: Could not open any camera (0-4). Please plug in a camera or set the correct --camera ID.")
            return False

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print(f"✅ Camera initialized (camera_id={self.camera_id})")
        return True
    
    def load_lstm_model(self, model_path: Optional[str]):
        """Load trained LSTM model"""
        if not model_path:
            print("⚠️ No LSTM model path provided; running pose detection without LSTM prediction.")
            self.lstm_model = None
            return

        if not os.path.exists(model_path):
            print(f"⚠️ LSTM model file not found at {model_path}; running pose detection without LSTM prediction.")
            self.lstm_model = None
            return

        self.lstm_model = YogaPoseLSTM()
        self.lstm_model.load_model(model_path)
        print(f"✅ Loaded LSTM model from {model_path}")
    
    def draw_info_panel(self, image: np.ndarray, analysis: Dict) -> np.ndarray:
        """Draw information panel on the image"""
        h, w = image.shape[:2]
        panel_width = 350
        panel_height = h
        
        # Create semi-transparent overlay
        overlay = image.copy()
        cv2.rectangle(overlay, (w - panel_width, 0), (w, panel_height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # Draw border
        cv2.rectangle(image, (w - panel_width, 0), (w, panel_height), 
                     self.colors['text'], 2)
        
        y_offset = 30
        
        # Title
        cv2.putText(image, "Yoga Pose Analysis", 
                   (w - panel_width + 10, y_offset),
                   self.font, self.font_scale + 0.2, self.colors['text'], self.thickness)
        y_offset += 40
        
        # LSTM Prediction
        if analysis.get('lstm_prediction'):
            cv2.putText(image, "LSTM Prediction:", 
                       (w - panel_width + 10, y_offset),
                       self.font, self.font_scale, self.colors['text'], self.thickness)
            y_offset += 25
            
            pred_text = f"{analysis['lstm_prediction']}"
            conf_text = f"Confidence: {analysis['lstm_confidence']:.2f}"
            
            cv2.putText(image, pred_text, 
                       (w - panel_width + 20, y_offset),
                       self.font, self.font_scale, self.colors['highlight'], self.thickness)
            y_offset += 25
            
            cv2.putText(image, conf_text, 
                       (w - panel_width + 20, y_offset),
                       self.font, self.font_scale, 
                       self.colors['good'] if analysis['lstm_confidence'] > 0.7 else self.colors['warning'], 
                       self.thickness)
            y_offset += 35
        
        # Reference Match
        if analysis.get('reference_match'):
            cv2.putText(image, "Reference Match:", 
                       (w - panel_width + 10, y_offset),
                       self.font, self.font_scale, self.colors['text'], self.thickness)
            y_offset += 25
            
            pose_name = analysis.get('pose_name', analysis['reference_match'])
            cv2.putText(image, pose_name, 
                       (w - panel_width + 20, y_offset),
                       self.font, self.font_scale, self.colors['good'], self.thickness)
            y_offset += 25
            
            # Accuracy score
            accuracy = analysis.get('accuracy_score', 0)
            accuracy_text = f"Accuracy: {accuracy:.1%}"
            color = self.colors['good'] if accuracy > 0.8 else self.colors['warning'] if accuracy > 0.6 else self.colors['error']
            cv2.putText(image, accuracy_text, 
                       (w - panel_width + 20, y_offset),
                       self.font, self.font_scale, color, self.thickness)
            y_offset += 35
        
        # Stability Score
        cv2.putText(image, "Stability:", 
                   (w - panel_width + 10, y_offset),
                   self.font, self.font_scale, self.colors['text'], self.thickness)
        y_offset += 25
        
        stability_text = f"{self.stability_score:.1%}"
        stability_color = self.colors['good'] if self.stability_score > 0.8 else self.colors['warning'] if self.stability_score > 0.6 else self.colors['error']
        cv2.putText(image, stability_text, 
                   (w - panel_width + 20, y_offset),
                   self.font, self.font_scale, stability_color, self.thickness)
        y_offset += 35
        
        # Feedback
        if analysis.get('overall_feedback'):
            cv2.putText(image, "Feedback:", 
                       (w - panel_width + 10, y_offset),
                       self.font, self.font_scale, self.colors['text'], self.thickness)
            y_offset += 25
            
            # Word wrap for long feedback
            feedback = analysis['overall_feedback']
            words = feedback.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                if len(test_line) > 40:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))
            
            for line in lines[:3]:  # Limit to 3 lines
                cv2.putText(image, line, 
                           (w - panel_width + 20, y_offset),
                           self.font, self.font_scale - 0.1, self.colors['text'], 1)
                y_offset += 20
            y_offset += 15
        
        # Improvement Tips
        if analysis.get('improvement_tips'):
            cv2.putText(image, "Tips:", 
                       (w - panel_width + 10, y_offset),
                       self.font, self.font_scale, self.colors['text'], self.thickness)
            y_offset += 25
            
            for i, tip in enumerate(analysis['improvement_tips'][:2]):  # Show top 2 tips
                cv2.putText(image, f"• {tip}", 
                           (w - panel_width + 20, y_offset),
                           self.font, self.font_scale - 0.1, self.colors['warning'], 1)
                y_offset += 20
        
        return image
    
    def draw_pose_skeleton(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Draw pose skeleton with angle highlights"""
        if landmarks is None:
            return image
        
        # Get current angles
        angles = self.pose_detector.get_key_angles(landmarks)
        
        # Draw landmarks and connections
        image = self.pose_detector.draw_landmarks(image, landmarks)
        
        # Highlight problematic joints
        analysis = self.pose_analyzer.analyze_pose(angles)
        angle_feedback = analysis.get('angle_feedback', {})
        
        # Highlight joints with high error
        mp_pose = self.pose_detector.mp_pose
        h, w = image.shape[:2]
        
        for joint, error in angle_feedback.items():
            if error > 0.3:  # High error threshold
                if 'elbow' in joint:
                    landmark_idx = 13 if 'left' in joint else 14
                elif 'knee' in joint:
                    landmark_idx = 25 if 'left' in joint else 26
                elif 'shoulder' in joint:
                    landmark_idx = 11 if 'left' in joint else 12
                else:
                    continue
                
                if len(landmarks) > landmark_idx * 4 + 1:
                    x = int(landmarks[landmark_idx * 4] * w)
                    y = int(landmarks[landmark_idx * 4 + 1] * h)
                    
                    # Draw highlight circle
                    cv2.circle(image, (x, y), 8, self.colors['error'], 3)
        
        return image
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Process a single frame"""
        # Extract landmarks
        landmarks = self.pose_detector.extract_landmarks(frame)
        
        analysis = {
            'landmarks_detected': landmarks is not None,
            'lstm_prediction': None,
            'lstm_confidence': 0.0,
            'reference_match': None,
            'accuracy_score': 0.0,
            'angle_feedback': {},
            'overall_feedback': '',
            'improvement_tips': []
        }
        
        if landmarks is not None:
            # Normalize landmarks
            normalized_landmarks = self.pose_detector.normalize_landmarks(landmarks)
            
            # Add to buffer
            self.landmarks_buffer.append(normalized_landmarks)
            if len(self.landmarks_buffer) > self.sequence_length * 2:
                self.landmarks_buffer.pop(0)
            
            # Get angles
            angles = self.pose_detector.get_key_angles(normalized_landmarks)
            
            # LSTM prediction
            if self.lstm_model and len(self.landmarks_buffer) >= self.sequence_length:
                pred_pose, confidence, _ = self.lstm_model.predict_realtime(self.landmarks_buffer)
                analysis['lstm_prediction'] = pred_pose
                analysis['lstm_confidence'] = confidence
            
            # Analyze pose
            analysis = self.pose_analyzer.analyze_pose(
                angles, 
                analysis.get('lstm_prediction'), 
                analysis.get('lstm_confidence', 0.0)
            )
            
            # Calculate stability
            self.stability_score = self.pose_analyzer.calculate_stability_score(self.landmarks_buffer)
            
            # Update current pose
            self.previous_pose = self.current_pose
            self.current_pose = analysis.get('reference_match')
            
            # Add to session data
            if analysis.get('reference_match'):
                self.session_data.append({
                    'timestamp': time.time(),
                    'pose': analysis['reference_match'],
                    'accuracy': analysis.get('accuracy_score', 0),
                    'stability': self.stability_score
                })
        
        # Draw on frame
        if landmarks is not None:
            frame = self.draw_pose_skeleton(frame, landmarks)
        
        frame = self.draw_info_panel(frame, analysis)
        
        return frame, analysis
    
    def run_camera(self, callback: Optional[Callable] = None):
        """Main camera loop"""
        if not self.initialize_camera():
            return
        
        print("Press 'q' to quit, 's' to save session data")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame
                processed_frame, analysis = self.process_frame(frame)
                
                # Custom callback if provided
                if callback:
                    callback(processed_frame, analysis)
                
                # Show frame
                cv2.imshow('Yoga Pose Estimation', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.save_session_data()
                elif key == ord('r'):
                    self.session_data.clear()
                    print("Session data cleared")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def save_session_data(self):
        """Save session data to file"""
        if not self.session_data:
            print("No session data to save")
            return
        
        timestamp = int(time.time())
        filename = f"yoga_session_{timestamp}.txt"
        
        summary = self.pose_analyzer.generate_session_summary(self.session_data)
        
        with open(filename, 'w') as f:
            f.write("Yoga Pose Session Summary\n")
            f.write("=" * 30 + "\n")
            f.write(f"Total Poses: {summary['total_poses']}\n")
            f.write(f"Average Accuracy: {summary['average_accuracy']:.1%}\n")
            f.write(f"Most Practiced: {summary['most_practiced']}\n")
            f.write(f"Improvement Trend: {summary['improvement_trend']}\n\n")
            
            f.write("Pose Distribution:\n")
            for pose, count in summary['pose_distribution'].items():
                f.write(f"  {pose}: {count}\n")
        
        print(f"Session data saved to {filename}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.pose_detector.close()
