import numpy as np
from typing import Dict, List, Tuple

class ReferencePoses:
    def __init__(self):
        # Define reference poses with key angles and landmarks
        self.poses = {
            'mountain_pose': {
                'name': 'Mountain Pose (Tadasana)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 180,
                    'right_knee': 180,
                    'left_shoulder': 90,
                    'right_shoulder': 90
                },
                'description': 'Standing straight with arms at sides',
                'difficulty': 'beginner'
            },
            'warrior_1': {
                'name': 'Warrior I (Virabhadrasana I)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 90,
                    'right_knee': 180,
                    'left_shoulder': 180,
                    'right_shoulder': 90
                },
                'description': 'Lunge with arms raised overhead',
                'difficulty': 'beginner'
            },
            'warrior_2': {
                'name': 'Warrior II (Virabhadrasana II)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 90,
                    'right_knee': 180,
                    'left_shoulder': 90,
                    'right_shoulder': 90
                },
                'description': 'Lunge with arms extended parallel to ground',
                'difficulty': 'beginner'
            },
            'tree_pose': {
                'name': 'Tree Pose (Vrikshasana)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 45,  # Standing leg
                    'right_knee': 90,  # Raised leg
                    'left_shoulder': 90,
                    'right_shoulder': 90
                },
                'description': 'Standing on one leg with other foot on inner thigh',
                'difficulty': 'intermediate'
            },
            'downward_dog': {
                'name': 'Downward Dog (Adho Mukha Svanasana)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 180,
                    'right_knee': 180,
                    'left_shoulder': 120,
                    'right_shoulder': 120
                },
                'description': 'Inverted V-shape with hands and feet on ground',
                'difficulty': 'beginner'
            },
            'child_pose': {
                'name': 'Child Pose (Balasana)',
                'key_angles': {
                    'left_elbow': 90,
                    'right_elbow': 90,
                    'left_knee': 90,
                    'right_knee': 90,
                    'left_shoulder': 180,
                    'right_shoulder': 180
                },
                'description': 'Kneeling with forehead on ground, arms extended or resting',
                'difficulty': 'beginner'
            },
            'cobra_pose': {
                'name': 'Cobra Pose (Bhujangasana)',
                'key_angles': {
                    'left_elbow': 45,
                    'right_elbow': 45,
                    'left_knee': 180,
                    'right_knee': 180,
                    'left_shoulder': 45,
                    'right_shoulder': 45
                },
                'description': 'Lying on stomach, chest lifted with arms supporting',
                'difficulty': 'beginner'
            },
            'triangle_pose': {
                'name': 'Triangle Pose (Trikonasana)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 180,
                    'right_knee': 180,
                    'left_shoulder': 90,
                    'right_shoulder': 90
                },
                'description': 'Wide-legged forward bend with one arm reaching down',
                'difficulty': 'intermediate'
            },
            'plank': {
                'name': 'Plank Pose',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 180,
                    'right_knee': 180,
                    'left_shoulder': 90,
                    'right_shoulder': 90
                },
                'description': 'Straight body position supported by arms and toes',
                'difficulty': 'beginner'
            },
            'bridge_pose': {
                'name': 'Bridge Pose (Setu Bandhasana)',
                'key_angles': {
                    'left_elbow': 180,
                    'right_elbow': 180,
                    'left_knee': 90,
                    'right_knee': 90,
                    'left_shoulder': 180,
                    'right_shoulder': 180
                },
                'description': 'Lying on back with hips lifted, arms supporting',
                'difficulty': 'beginner'
            }
        }
    
    def get_pose_angles(self, pose_name: str) -> Dict[str, float]:
        """Get reference angles for a specific pose"""
        if pose_name in self.poses:
            return self.poses[pose_name]['key_angles']
        return {}
    
    def get_all_pose_names(self) -> List[str]:
        """Get all available pose names"""
        return list(self.poses.keys())
    
    def get_pose_info(self, pose_name: str) -> Dict:
        """Get complete information about a pose"""
        if pose_name in self.poses:
            return self.poses[pose_name]
        return {}
    
    def calculate_pose_similarity(self, detected_angles: Dict[str, float], 
                                 reference_pose: str) -> Tuple[float, Dict[str, float]]:
        """Calculate similarity score between detected pose and reference"""
        if reference_pose not in self.poses:
            return 0.0, {}
        
        reference_angles = self.poses[reference_pose]['key_angles']
        angle_differences = {}
        total_error = 0
        valid_angles = 0
        
        for joint, ref_angle in reference_angles.items():
            if joint in detected_angles:
                detected_angle = detected_angles[joint]
                difference = abs(detected_angle - ref_angle)
                
                # Normalize difference (max difference is 180 degrees)
                normalized_diff = min(difference / 180.0, 1.0)
                angle_differences[joint] = normalized_diff
                
                total_error += normalized_diff
                valid_angles += 1
        
        if valid_angles == 0:
            return 0.0, {}
        
        # Calculate accuracy (1 - average normalized error)
        accuracy = 1.0 - (total_error / valid_angles)
        accuracy = max(0.0, min(1.0, accuracy))  # Clamp between 0 and 1
        
        return accuracy, angle_differences
    
    def get_best_match(self, detected_angles: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """Find the best matching pose for detected angles"""
        best_pose = None
        best_score = 0.0
        best_differences = {}
        
        for pose_name in self.poses.keys():
            score, differences = self.calculate_pose_similarity(detected_angles, pose_name)
            if score > best_score:
                best_score = score
                best_pose = pose_name
                best_differences = differences
        
        return best_pose, best_score, best_differences
    
    def get_poses_by_difficulty(self, difficulty: str) -> List[str]:
        """Get poses filtered by difficulty level"""
        return [name for name, info in self.poses.items() 
                if info['difficulty'] == difficulty]
