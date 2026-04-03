import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def extract_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract pose landmarks from image"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if results.pose_landmarks:
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
            return np.array(landmarks)
        return None
    
    def draw_landmarks(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Draw pose landmarks on image"""
        if landmarks is not None:
            # Create a dummy pose landmarks object for drawing
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return image
    
    def normalize_landmarks(self, landmarks: np.ndarray) -> np.ndarray:
        """Normalize landmarks relative to hip center"""
        if landmarks is None or len(landmarks) == 0:
            return landmarks
            
        # Hip center is average of left and right hip (landmarks 23 and 24)
        left_hip_idx = 23 * 4
        right_hip_idx = 24 * 4
        
        hip_center_x = (landmarks[left_hip_idx] + landmarks[right_hip_idx]) / 2
        hip_center_y = (landmarks[left_hip_idx + 1] + landmarks[right_hip_idx + 1]) / 2
        
        # Normalize all landmarks relative to hip center
        normalized = landmarks.copy()
        for i in range(0, len(normalized), 4):
            normalized[i] -= hip_center_x  # x
            normalized[i + 1] -= hip_center_y  # y
        
        return normalized
    
    def get_key_angles(self, landmarks: np.ndarray) -> dict:
        """Calculate key joint angles from landmarks"""
        if landmarks is None or len(landmarks) < 33 * 4:
            return {}
        
        angles = {}
        
        # Helper function to calculate angle between three points
        def calculate_angle(p1, p2, p3):
            v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            return np.degrees(angle)
        
        # Left elbow angle (shoulder-elbow-wrist)
        left_shoulder = landmarks[11*4:11*4+2]
        left_elbow = landmarks[13*4:13*4+2]
        left_wrist = landmarks[15*4:15*4+2]
        angles['left_elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
        
        # Right elbow angle
        right_shoulder = landmarks[12*4:12*4+2]
        right_elbow = landmarks[14*4:14*4+2]
        right_wrist = landmarks[16*4:16*4+2]
        angles['right_elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Left knee angle (hip-knee-ankle)
        left_hip = landmarks[23*4:23*4+2]
        left_knee = landmarks[25*4:25*4+2]
        left_ankle = landmarks[27*4:27*4+2]
        angles['left_knee'] = calculate_angle(left_hip, left_knee, left_ankle)
        
        # Right knee angle
        right_hip = landmarks[24*4:24*4+2]
        right_knee = landmarks[26*4:26*4+2]
        right_ankle = landmarks[28*4:28*4+2]
        angles['right_knee'] = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Left shoulder angle (elbow-shoulder-hip)
        angles['left_shoulder'] = calculate_angle(left_elbow, left_shoulder, left_hip)
        
        # Right shoulder angle
        angles['right_shoulder'] = calculate_angle(right_elbow, right_shoulder, right_hip)
        
        return angles
    
    def close(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'pose') and self.pose is not None:
                self.pose.close()
                print("✅ Pose detector resources cleaned up")
            else:
                print("⚠️  Pose detector was not initialized")
        except Exception as e:
            print(f"⚠️  Error closing pose detector: {e}")
