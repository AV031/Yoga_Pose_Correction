# Yoga Pose Estimation System

A comprehensive computer vision system for real-time yoga pose estimation using LSTM neural networks and MediaPipe pose detection.

## Features

- **Real-time Pose Detection**: Uses MediaPipe for accurate skeletal landmark extraction
- **LSTM Classification**: Deep learning model for pose sequence classification
- **Accuracy Scoring**: Real-time comparison with reference poses
- **Live Camera Feed**: Interactive visualization with feedback
- **Pose Database**: 10 predefined yoga poses with reference angles
- **Session Tracking**: Monitor progress and save session data

## Supported Yoga Poses

1. **Mountain Pose** (Tadasana) - Beginner
2. **Warrior I** (Virabhadrasana I) - Beginner
3. **Warrior II** (Virabhadrasana II) - Beginner
4. **Tree Pose** (Vrikshasana) - Intermediate
5. **Downward Dog** (Adho Mukha Svanasana) - Beginner
6. **Child Pose** (Balasana) - Beginner
7. **Cobra Pose** (Bhujangasana) - Beginner
8. **Triangle Pose** (Trikonasana) - Intermediate
9. **Plank Pose** - Beginner
10. **Bridge Pose** (Setu Bandhasana) - Beginner

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Train the Model
```bash
python main.py --mode train
```

### 2. Run Live Demo
```bash
python main.py --mode demo
```

### 3. Collect Training Data
```bash
python main.py --mode collect
```

## Usage

### Live Demo Mode
- Press 'q' to quit
- Press 's' to save session data
- Press 'r' to reset session data

The interface shows:
- **LSTM Prediction**: AI classification confidence
- **Reference Match**: Best matching pose from database
- **Accuracy Score**: Real-time pose accuracy percentage
- **Stability Score**: Pose stability measurement
- **Feedback**: Real-time improvement suggestions
- **Tips**: Specific joint corrections

### Data Collection Mode
1. Select a pose from the menu
2. Hold the pose for 30 seconds
3. System collects landmark data
4. Repeat for multiple poses
5. Optionally train a model with collected data

### Analysis Mode
Analyze previously collected data files to evaluate pose accuracy and get performance insights.

## Project Structure

```
yoga_pose_estimator/
├── main.py              # Main application entry point
├── pose_detector.py     # MediaPipe pose detection
├── lstm_model.py        # LSTM neural network model
├── reference_poses.py   # Reference pose database
├── pose_analyzer.py     # Pose analysis and scoring
├── camera_interface.py  # Live camera interface
├── train_model.py       # Model training script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Technical Details

### Pose Detection
- Uses MediaPipe Pose for 33 skeletal landmarks
- Normalizes landmarks relative to hip center
- Calculates key joint angles (elbows, knees, shoulders)

### LSTM Model
- 3-layer LSTM architecture with dropout
- Input: 30-frame sequences (132 features per frame)
- Output: Multi-class pose classification
- Trained on synthetic and real pose data

### Accuracy Scoring
- Compares detected angles with reference poses
- Calculates similarity scores for each joint
- Provides overall pose accuracy percentage
- Generates specific improvement feedback

### Real-time Features
- 30 FPS camera processing
- Live skeletal overlay
- Real-time accuracy updates
- Stability tracking
- Session performance summary

## Model Architecture

```
Input (30, 132)
├── LSTM(128) → BatchNorm → Dropout(0.3)
├── LSTM(64) → BatchNorm → Dropout(0.3)
├── LSTM(32) → BatchNorm → Dropout(0.3)
├── Dense(64) → BatchNorm → Dropout(0.2)
├── Dense(32) → Dropout(0.2)
└── Dense(num_classes) → Softmax
```

## Data Format

### Landmark Features
- 33 pose landmarks × 4 features (x, y, z, visibility) = 132 features
- Normalized coordinates relative to hip center
- Sequence length: 30 frames

### Reference Pose Angles
- Left/Right elbow angles
- Left/Right knee angles
- Left/Right shoulder angles
- Measured in degrees

## Performance

- **Accuracy**: ~85-90% on test data
- **Latency**: <50ms per frame
- **Memory**: ~500MB RAM usage
- **FPS**: 25-30 FPS on modern hardware

## Troubleshooting

### Camera Issues
- Check camera connection and permissions
- Try different camera IDs (0, 1, 2...)
- Ensure adequate lighting

### Model Performance
- Retrain with more diverse data
- Adjust sequence length (20-40 frames)
- Fine-tune hyperparameters

### Accuracy Issues
- Ensure proper pose alignment
- Check camera angle and distance
- Verify reference pose angles

## Contributing

1. Add new reference poses to `reference_poses.py`
2. Collect training data for new poses
3. Retrain the LSTM model
4. Update class names and documentation

## License

This project is for educational and research purposes. Please refer to individual library licenses for usage terms.

## Acknowledgments

- MediaPipe for pose detection
- TensorFlow for deep learning
- OpenCV for computer vision
- Yoga reference data from various sources
