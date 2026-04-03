import cv2
import numpy as np
import json
from typing import List, Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tqdm import tqdm

from pose_detector import PoseDetector
from lstm_model import YogaPoseLSTM
from reference_poses import ReferencePoses

class DataCollector:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.reference_poses = ReferencePoses()
        self.collected_data = {}
        
    def collect_from_video(self, video_path: str, pose_name: str, 
                          max_frames: int = 500) -> List[np.ndarray]:
        """Collect pose data from video file"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return []
        
        landmarks_list = []
        frame_count = 0
        
        print(f"Collecting data for {pose_name} from {video_path}")
        
        with tqdm(total=max_frames, desc=f"Processing {pose_name}") as pbar:
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                landmarks = self.pose_detector.extract_landmarks(frame)
                if landmarks is not None:
                    normalized = self.pose_detector.normalize_landmarks(landmarks)
                    landmarks_list.append(normalized)
                
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        print(f"Collected {len(landmarks_list)} valid frames for {pose_name}")
        return landmarks_list
    
    def collect_from_camera(self, pose_name: str, duration_seconds: int = 30) -> List[np.ndarray]:
        """Collect pose data from live camera"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return []
        
        landmarks_list = []
        start_time = cv2.getTickCount()
        
        print(f"Collecting data for {pose_name} - Hold the pose for {duration_seconds} seconds")
        print("Press 'q' to stop early")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Calculate elapsed time
            elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed >= duration_seconds:
                break
            
            landmarks = self.pose_detector.extract_landmarks(frame)
            if landmarks is not None:
                normalized = self.pose_detector.normalize_landmarks(landmarks)
                landmarks_list.append(normalized)
                
                # Draw landmarks on frame
                frame = self.pose_detector.draw_landmarks(frame, landmarks)
                
                # Show progress
                progress = elapsed / duration_seconds
                cv2.putText(frame, f"Collecting {pose_name}: {progress:.1%}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Data Collection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"Collected {len(landmarks_list)} frames for {pose_name}")
        return landmarks_list
    
    def save_collected_data(self, data: Dict[str, List[np.ndarray]], filepath: str):
        """Save collected data to file"""
        processed_data = {}
        for pose_name, landmarks_list in data.items():
            processed_data[pose_name] = [landmarks.tolist() for landmarks in landmarks_list]
        
        with open(filepath, 'w') as f:
            json.dump(processed_data, f)
        
        print(f"Data saved to {filepath}")
    
    def load_collected_data(self, filepath: str) -> Dict[str, List[np.ndarray]]:
        """Load collected data from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        processed_data = {}
        for pose_name, landmarks_list in data.items():
            processed_data[pose_name] = [np.array(landmarks) for landmarks in landmarks_list]
        
        return processed_data

class ModelTrainer:
    def __init__(self, sequence_length: int = 30):
        self.sequence_length = sequence_length
        self.label_encoder = LabelEncoder()
        
    def prepare_training_data(self, collected_data: Dict[str, List[np.ndarray]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare data for training"""
        X_sequences = []
        y_labels = []
        
        print("Preparing training sequences...")
        
        for pose_name, landmarks_list in tqdm(collected_data.items(), desc="Processing poses"):
            # Create sequences
            for i in range(len(landmarks_list) - self.sequence_length + 1):
                sequence = landmarks_list[i:i + self.sequence_length]
                X_sequences.append(sequence)
                y_labels.append(pose_name)
        
        X = np.array(X_sequences)
        y = np.array(y_labels)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        class_names = self.label_encoder.classes_.tolist()
        
        print(f"Prepared {len(X)} sequences for {len(class_names)} classes")
        return X, y_encoded, class_names
    
    def train_model(self, X: np.ndarray, y: np.ndarray, class_names: List[str],
                   model_save_path: str = "yoga_pose_lstm.h5") -> Dict:
        """Train the LSTM model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Further split training set for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        print(f"Training set: {len(X_train)} sequences")
        print(f"Validation set: {len(X_val)} sequences")
        print(f"Test set: {len(X_test)} sequences")
        
        # Create model
        model = YogaPoseLSTM(
            sequence_length=self.sequence_length,
            num_features=X.shape[2],
            num_classes=len(class_names)
        )
        model.set_class_names(class_names)
        
        # Train model
        print("Training LSTM model...")
        history = model.train(X_train, y_train, X_val, y_val, epochs=50, batch_size=32)
        
        # Evaluate model
        print("Evaluating model...")
        test_loss, test_accuracy, test_top_k = model.model.evaluate(X_test, 
                                                                   tf.keras.utils.to_categorical(y_test, len(class_names)),
                                                                   verbose=0)
        
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test Top-K Accuracy: {test_top_k:.4f}")
        
        # Save model
        model.save_model(model_save_path)
        print(f"Model saved to {model_save_path}")
        
        return {
            'model': model,
            'history': history,
            'test_accuracy': test_accuracy,
            'test_top_k_accuracy': test_top_k,
            'class_names': class_names
        }

def create_synthetic_training_data(output_path: str = "synthetic_yoga_data.json"):
    """Create synthetic training data based on reference poses"""
    collector = DataCollector()
    reference_poses = ReferencePoses()
    
    synthetic_data = {}
    
    print("Creating synthetic training data...")
    
    for pose_name in tqdm(reference_poses.get_all_pose_names(), desc="Generating poses"):
        # Generate synthetic landmarks that match target angles
        # This is a simplified approach - in practice, you'd want more sophisticated generation
        landmarks_list = []
        
        for _ in range(200):  # Generate 200 samples per pose
            # Create base landmarks (33 points * 4 features = 132 features)
            landmarks = np.random.randn(132) * 0.1  # Small random variation
            
            # Modify key landmarks to match target angles (simplified)
            # In a real implementation, you'd use inverse kinematics or similar
            
            landmarks_list.append(landmarks)
        
        synthetic_data[pose_name] = landmarks_list
    
    # Save synthetic data
    collector.save_collected_data(synthetic_data, output_path)
    print(f"Synthetic data saved to {output_path}")
    
    return synthetic_data

def main():
    """Main training function"""
    print("Yoga Pose LSTM Model Training")
    print("=" * 40)
    
    # Create synthetic data for demonstration
    print("\nStep 1: Creating synthetic training data...")
    synthetic_data = create_synthetic_training_data()
    
    # Train model
    print("\nStep 2: Training LSTM model...")
    trainer = ModelTrainer(sequence_length=30)
    
    X, y, class_names = trainer.prepare_training_data(synthetic_data)
    
    results = trainer.train_model(X, y, class_names, "yoga_pose_lstm.h5")
    
    print("\nTraining completed!")
    print(f"Final test accuracy: {results['test_accuracy']:.4f}")
    print(f"Classes: {class_names}")
    
    # Test with sample data
    print("\nStep 3: Testing model...")
    model = results['model']
    
    # Test with a sample sequence
    sample_sequence = X[0:1]  # Take first sequence
    prediction, confidence, probs = model.predict(sample_sequence[0])
    
    print(f"Sample prediction: {prediction} with confidence {confidence:.4f}")

if __name__ == "__main__":
    main()
