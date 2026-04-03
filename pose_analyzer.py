import numpy as np
from typing import Dict, Tuple, List
from reference_poses import ReferencePoses

class PoseAnalyzer:
    def __init__(self):
        self.reference_poses = ReferencePoses()
        self.confidence_threshold = 0.5
        self.angle_tolerance = 15.0  # degrees
    
    def analyze_pose(self, detected_angles: Dict[str, float], 
                    lstm_prediction: str = None, 
                    lstm_confidence: float = 0.0) -> Dict:
        """Analyze detected pose and provide comprehensive feedback"""
        analysis = {
            'detected_angles': detected_angles,
            'lstm_prediction': lstm_prediction,
            'lstm_confidence': lstm_confidence,
            'reference_match': None,
            'accuracy_score': 0.0,
            'angle_feedback': {},
            'overall_feedback': '',
            'improvement_tips': []
        }
        
        # Find best matching reference pose
        best_pose, best_score, angle_diffs = self.reference_poses.get_best_match(detected_angles)
        
        if best_pose:
            analysis['reference_match'] = best_pose
            analysis['accuracy_score'] = best_score
            analysis['angle_feedback'] = angle_diffs
            
            # Get pose information
            pose_info = self.reference_poses.get_pose_info(best_pose)
            analysis['pose_name'] = pose_info.get('name', best_pose)
            analysis['pose_description'] = pose_info.get('description', '')
            analysis['difficulty'] = pose_info.get('difficulty', 'unknown')
            
            # Generate feedback
            analysis['overall_feedback'] = self._generate_overall_feedback(best_score)
            analysis['improvement_tips'] = self._generate_improvement_tips(
                detected_angles, best_pose, angle_diffs)
        
        return analysis

    def calculate_accuracy(self, detected_angles: Dict[str, float], reference_pose: object) -> float:
        """Calculate accuracy against a reference pose definition or name."""
        if not detected_angles:
            return 0.0

        if isinstance(reference_pose, str):
            reference_pose_data = self.reference_poses.get_pose_info(reference_pose)
        elif isinstance(reference_pose, dict):
            reference_pose_data = reference_pose
        else:
            reference_pose_data = {}

        key_angles = reference_pose_data.get('key_angles') if isinstance(reference_pose_data, dict) else None
        if not key_angles:
            return 0.0

        # Calculate normalized error across key angles
        total_error = 0.0
        matched = 0
        for joint, target_angle in key_angles.items():
            if joint in detected_angles:
                diff = abs(detected_angles[joint] - target_angle)
                total_error += min(diff / 180.0, 1.0)
                matched += 1

        if matched == 0:
            return 0.0

        accuracy = 1.0 - (total_error / matched)
        return max(0.0, min(1.0, accuracy))
    
    def _generate_overall_feedback(self, accuracy_score: float) -> str:
        """Generate overall feedback based on accuracy score"""
        if accuracy_score >= 0.9:
            return "Excellent! Your pose is nearly perfect."
        elif accuracy_score >= 0.8:
            return "Great job! Your pose is very good with minor adjustments needed."
        elif accuracy_score >= 0.7:
            return "Good effort! Focus on the highlighted areas for improvement."
        elif accuracy_score >= 0.6:
            return "Getting there! Pay attention to the suggested corrections."
        else:
            return "Keep practicing! Focus on the fundamental alignment."
    
    def _generate_improvement_tips(self, detected_angles: Dict[str, float], 
                                  pose_name: str, angle_diffs: Dict[str, float]) -> List[str]:
        """Generate specific improvement tips based on angle differences"""
        tips = []
        reference_angles = self.reference_poses.get_pose_angles(pose_name)
        
        for joint, diff in angle_diffs.items():
            if diff > 0.3:  # Significant difference (>30% error)
                detected = detected_angles.get(joint, 0)
                reference = reference_angles.get(joint, 0)
                
                if joint == 'left_elbow' or joint == 'right_elbow':
                    if detected < reference:
                        tips.append(f"Straighten your {'left' if 'left' in joint else 'right'} arm more")
                    else:
                        tips.append(f"Bend your {'left' if 'left' in joint else 'right'} elbow slightly")
                
                elif joint == 'left_knee' or joint == 'right_knee':
                    if detected < reference:
                        tips.append(f"Straighten your {'left' if 'left' in joint else 'right'} leg more")
                    else:
                        tips.append(f"Bend your {'left' if 'left' in joint else 'right'} knee more")
                
                elif joint == 'left_shoulder' or joint == 'right_shoulder':
                    if detected < reference:
                        tips.append(f"Raise your {'left' if 'left' in joint else 'right'} arm higher")
                    else:
                        tips.append(f"Lower your {'left' if 'left' in joint else 'right'} arm slightly")
        
        if not tips:
            tips.append("Maintain your current position and focus on breathing")
        
        return tips
    
    def calculate_stability_score(self, landmarks_buffer: List[np.ndarray]) -> float:
        """Calculate pose stability based on recent frames"""
        if len(landmarks_buffer) < 5:
            return 0.0
        
        # Calculate variance in key landmarks over recent frames
        recent_frames = landmarks_buffer[-5:]
        key_landmarks = [11, 12, 23, 24, 15, 16, 27, 28]  # Shoulders, hips, wrists, ankles
        
        total_variance = 0
        for landmark_idx in key_landmarks:
            positions = []
            for frame in recent_frames:
                if len(frame) > landmark_idx * 4 + 1:
                    positions.append([frame[landmark_idx * 4], frame[landmark_idx * 4 + 1]])
            
            if len(positions) >= 2:
                positions = np.array(positions)
                variance = np.var(positions)
                total_variance += variance
        
        # Normalize stability score (lower variance = higher stability)
        stability = max(0, 1 - total_variance / len(key_landmarks))
        return stability
    
    def detect_transition(self, current_pose: str, previous_pose: str, 
                         confidence: float) -> bool:
        """Detect if user is transitioning between poses"""
        if confidence < 0.5:  # Low confidence indicates transition
            return True
        
        if current_pose != previous_pose and previous_pose is not None:
            return True
        
        return False
    
    def get_pose_difficulty_feedback(self, pose_name: str, accuracy_score: float) -> str:
        """Provide feedback based on pose difficulty and performance"""
        pose_info = self.reference_poses.get_pose_info(pose_name)
        difficulty = pose_info.get('difficulty', 'beginner')
        
        if difficulty == 'beginner':
            if accuracy_score >= 0.8:
                return "Great! You're ready to try intermediate poses."
            else:
                return "Focus on mastering this foundational pose first."
        
        elif difficulty == 'intermediate':
            if accuracy_score >= 0.8:
                return "Excellent! You're ready for advanced poses."
            else:
                return "This is challenging - keep practicing the basics."
        
        else:  # advanced
            if accuracy_score >= 0.8:
                return "Outstanding! You've mastered an advanced pose."
            else:
                return "Advanced poses require patience and practice."
    
    def generate_session_summary(self, session_data: List[Dict]) -> Dict:
        """Generate summary of a practice session"""
        if not session_data:
            return {'total_poses': 0, 'average_accuracy': 0, 'most_practiced': None}
        
        total_poses = len(session_data)
        accuracies = [data.get('accuracy_score', 0) for data in session_data]
        average_accuracy = np.mean(accuracies)
        
        # Count pose occurrences
        pose_counts = {}
        for data in session_data:
            pose = data.get('reference_match', 'unknown')
            pose_counts[pose] = pose_counts.get(pose, 0) + 1
        
        most_practiced = max(pose_counts.items(), key=lambda x: x[1])[0] if pose_counts else None
        
        return {
            'total_poses': total_poses,
            'average_accuracy': average_accuracy,
            'most_practiced': most_practiced,
            'pose_distribution': pose_counts,
            'improvement_trend': self._calculate_improvement_trend(accuracies)
        }
    
    def _calculate_improvement_trend(self, accuracies: List[float]) -> str:
        """Calculate if user is improving over the session"""
        if len(accuracies) < 3:
            return "insufficient_data"
        
        first_half = np.mean(accuracies[:len(accuracies)//2])
        second_half = np.mean(accuracies[len(accuracies)//2:])
        
        if second_half > first_half + 0.1:
            return "improving"
        elif second_half < first_half - 0.1:
            return "declining"
        else:
            return "stable"
