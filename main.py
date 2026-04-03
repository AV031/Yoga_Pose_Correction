#!/usr/bin/env python3
"""
Yoga Pose Estimation System
Main application entry point
"""

import os
import sys
import argparse
import time
from typing import Optional

from camera_interface import CameraInterface
from train_model import DataCollector, ModelTrainer, create_synthetic_training_data
from pose_analyzer import PoseAnalyzer
from reference_poses import ReferencePoses

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           YOGA POSE ESTIMATION SYSTEM                        ║
    ║                                                              ║
    ║    Real-time pose detection with LSTM classification         ║
    ║    and accuracy scoring                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'cv2', 'mediapipe', 'tensorflow', 'numpy', 
        'sklearn', 'matplotlib', 'pillow', 'tqdm', 'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'sklearn':
                import sklearn
            elif package == 'pillow':
                from PIL import Image
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def setup_model():
    """Setup or train the LSTM model"""
    model_path = "yoga_pose_lstm.h5"
    
    if os.path.exists(model_path):
        print(f"✅ Found existing model: {model_path}")
        return model_path
    else:
        print("❌ No trained model found")
        choice = input("Would you like to train a new model? (y/n): ").lower()

        if choice == 'y':
            print("Training new model...")
            try:
                # Create synthetic training data
                synthetic_data = create_synthetic_training_data()

                # Train the model
                trainer = ModelTrainer(sequence_length=30)
                X, y, class_names = trainer.prepare_training_data(synthetic_data)
                results = trainer.train_model(X, y, class_names, model_path)

                print(f"✅ Model trained and saved to {model_path}")
                print(f"   Test accuracy: {results['test_accuracy']:.4f}")
                return model_path

            except Exception as e:
                print(f"❌ Error training model: {e}")
                return None

        else:
            fallback = input("Continue without LSTM model (pose detection only)? (y/n): ").lower()
            if fallback == 'y':
                print("⚠️ Running without LSTM model. Pose detection will still work, but classification may be disabled.")
                return None
            else:
                print("❌ Cannot proceed without a trained model")
                return None

def run_live_demo(camera_id: int = 0):
    """Run live camera demo"""
    print("\n" + "="*50)
    print("LIVE YOGA POSE ESTIMATION DEMO")
    print("="*50)
    print("\nControls:")
    print("  - 'q': Quit the application")
    print("  - 's': Save session data")
    print("  - 'r': Reset session data")
    print("\nStarting camera...")
    
    # Setup model
    model_path = setup_model()

    # Initialize camera interface
    camera = CameraInterface(camera_id=camera_id)

    if model_path:
        camera.load_lstm_model(model_path)
    else:
        camera.load_lstm_model(None)
    
    try:
        camera.run_camera()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

def collect_training_data():
    """Collect training data from camera"""
    print("\n" + "="*50)
    print("TRAINING DATA COLLECTION")
    print("="*50)
    
    collector = DataCollector()
    reference_poses = ReferencePoses()
    
    collected_data = {}
    
    print("Available poses:")
    poses = reference_poses.get_all_pose_names()
    for i, pose in enumerate(poses, 1):
        pose_info = reference_poses.get_pose_info(pose)
        print(f"  {i}. {pose_info['name']} ({pose_info['difficulty']})")
    
    while True:
        try:
            choice = input(f"\nSelect pose (1-{len(poses)}) or 'q' to finish: ").lower()
            
            if choice == 'q':
                break
            
            pose_idx = int(choice) - 1
            if 0 <= pose_idx < len(poses):
                pose_name = poses[pose_idx]
                pose_info = reference_poses.get_pose_info(pose_name)
                
                print(f"\nCollecting data for: {pose_info['name']}")
                print(f"Description: {pose_info['description']}")
                print("\nGet ready to hold the pose...")
                input("Press Enter when ready")
                
                # Collect data
                landmarks = collector.collect_from_camera(pose_name, duration_seconds=30)
                
                if landmarks:
                    collected_data[pose_name] = landmarks
                    print(f"✅ Collected {len(landmarks)} frames")
                else:
                    print("❌ No data collected")
            else:
                print("Invalid selection")
                
        except ValueError:
            print("Invalid input")
        except KeyboardInterrupt:
            break
    
    if collected_data:
        # Save collected data
        timestamp = int(time.time())
        filename = f"collected_yoga_data_{timestamp}.json"
        collector.save_collected_data(collected_data, filename)
        
        # Ask if user wants to train model
        train_choice = input("\nWould you like to train a model with this data? (y/n): ").lower()
        if train_choice == 'y':
            trainer = ModelTrainer(sequence_length=30)
            X, y, class_names = trainer.prepare_training_data(collected_data)
            results = trainer.train_model(X, y, class_names, "yoga_pose_lstm.h5")
            print(f"✅ Model trained with accuracy: {results['test_accuracy']:.4f}")

def show_reference_poses():
    """Display reference poses information"""
    print("\n" + "="*50)
    print("REFERENCE YOGA POSES")
    print("="*50)
    
    reference_poses = ReferencePoses()
    
    for pose_name in reference_poses.get_all_pose_names():
        pose_info = reference_poses.get_pose_info(pose_name)
        print(f"\n🧘 {pose_info['name']}")
        print(f"   Difficulty: {pose_info['difficulty']}")
        print(f"   Description: {pose_info['description']}")
        print(f"   Key Angles: {pose_info['key_angles']}")

def run_batch_analysis():
    """Run analysis on collected data"""
    print("\n" + "="*50)
    print("BATCH POSE ANALYSIS")
    print("="*50)
    
    # List available data files
    data_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not data_files:
        print("No data files found. Please collect training data first.")
        return
    
    print("Available data files:")
    for i, file in enumerate(data_files, 1):
        print(f"  {i}. {file}")
    
    try:
        choice = input(f"Select file (1-{len(data_files)}): ")
        file_idx = int(choice) - 1
        
        if 0 <= file_idx < len(data_files):
            filename = data_files[file_idx]
            
            # Load and analyze data
            collector = DataCollector()
            data = collector.load_collected_data(filename)
            
            analyzer = PoseAnalyzer()
            
            print(f"\nAnalyzing {filename}...")
            print(f"Found {len(data)} poses")
            
            for pose_name, landmarks_list in data.items():
                if landmarks_list:
                    # Sample a few landmarks for analysis
                    sample_landmarks = landmarks_list[0]
                    angles = collector.pose_detector.get_key_angles(sample_landmarks)
                    analysis = analyzer.analyze_pose(angles)
                    
                    print(f"\n{pose_name}:")
                    print(f"  Best match: {analysis.get('reference_match', 'Unknown')}")
                    print(f"  Accuracy: {analysis.get('accuracy_score', 0):.1%}")
                    print(f"  Feedback: {analysis.get('overall_feedback', '')}")
        
    except (ValueError, IndexError, FileNotFoundError) as e:
        print(f"Error: {e}")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Yoga Pose Estimation System')
    parser.add_argument('--mode', choices=['demo', 'train', 'collect', 'poses', 'analyze'], 
                       default='demo', help='Application mode')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    parser.add_argument('--model', type=str, default='yoga_pose_lstm.h5', help='Model file path')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run based on mode
    if args.mode == 'demo':
        run_live_demo(camera_id=args.camera)
    elif args.mode == 'train':
        setup_model()
    elif args.mode == 'collect':
        collect_training_data()
    elif args.mode == 'poses':
        show_reference_poses()
    elif args.mode == 'analyze':
        run_batch_analysis()
    
    print("\nThank you for using Yoga Pose Estimation System! 🧘")

if __name__ == "__main__":
    main()
