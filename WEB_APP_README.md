# Yoga Pose Estimator - Web Application

A professional, full-featured web application for real-time yoga pose estimation using AI and computer vision.

## 🎯 Features

### Real-Time Pose Detection
- **Live Webcam Feed**: Direct camera integration with real-time processing
- **33-Point Skeleton Detection**: MediaPipe-powered skeletal landmark detection
- **LSTM Classification**: Deep learning model for accurate pose recognition

### Professional User Interface
- **Modern Dashboard**: Beautiful, responsive UI with gradient designs
- **Real-Time Metrics**: Live angle measurements and stability scores
- **Accuracy Scoring**: Real-time comparison with reference poses
- **Smart Feedback**: Personalized corrections and tips

### Session Management
- **Session Tracking**: Monitor duration, frames, and accuracy
- **Progress Analytics**: Track improvement over time
- **Session History**: Browse and review past sessions
- **Data Export**: Save sessions as JSON for analysis

### Supported Yoga Poses
1. **Mountain Pose** (Tadasana) - Standing
2. **Warrior I** (Virabhadrasana I) - Standing
3. **Warrior II** (Virabhadrasana II) - Standing
4. **Tree Pose** (Vrikshasana) - Balance
5. **Downward Dog** (Adho Mukha Svanasana) - Inversion
6. **Child Pose** (Balasana) - Resting
7. **Cobra Pose** (Bhujangasana) - Backbend
8. **Triangle Pose** (Trikonasana) - Standing
9. **Plank Pose** - Core
10. **Bridge Pose** (Setu Bandhasana) - Backbend

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam for pose detection
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Yoga_Pose_Correction.git
cd Yoga_Pose_Correction
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
```
http://localhost:5000
```

## 📖 Usage Guide

### Starting a Session

1. Navigate to **Live Session** tab
2. Click **Start Capture** button
3. Allow camera access when prompted
4. Position yourself in front of the camera
5. The system will start detecting poses in real-time

### Real-Time Feedback

The application provides:
- **Pose Name**: Current detected yoga pose
- **Confidence Score**: AI model confidence (0-100%)
- **Accuracy Percentage**: Comparison with reference pose
- **Joint Angles**: Real-time measurements of key joints
  - Shoulder angle
  - Elbow angle
  - Knee angle
  - Stability score
- **Live Feedback**: Specific tips for pose correction

### Viewing History

1. Navigate to **History** tab
2. Filter by time period (All, Today, Week, Month)
3. View session statistics:
   - Session duration
   - Total frames processed
   - Unique poses detected
   - Average accuracy
   - Best accuracy achieved

### Saving Sessions

- Click **Save Session** to download session data as JSON
- Sessions are automatically saved when you end a session

## 🏗️ Architecture

### Backend (Flask + Socket.io)

The backend handles:
- **Real-time communication** via WebSocket
- **Pose detection** using MediaPipe
- **LSTM classification** for pose recognition
- **Session management** and data persistence
- **Angle calculations** for joint analysis

### Frontend (HTML5 + CSS + JavaScript)

The frontend provides:
- **Responsive UI** with modern design patterns
- **Real-time Canvas rendering** for video and overlays
- **Socket.io client** for live communication
- **Responsive grid system** that works on all devices

### Key Components

```
app.py                          - Flask application & API endpoints
templates/
  ├── index.html               - Main HTML structure
static/
  ├── css/
  │   └── style.css            - Modern CSS styling
  └── js/
      ├── main.js              - Core functionality
      └── session.js           - Session & capture logic
```

## 📡 API Endpoints

### Session Management

```
POST /api/session/start           - Start a new session
POST /api/session/<id>/end        - End active session
GET /api/session/<id>/summary     - Get session summary
GET /api/sessions                 - Get all saved sessions
```

### Pose Information

```
GET /api/poses                    - Get supported poses
```

### Health Check

```
GET /api/health                   - Server health status
```

## 🔌 WebSocket Events

### Client → Server

```
process_frame          - Send video frame for processing
start_pose_detection   - Initialize pose detection
```

### Server → Client

```
pose_detected         - Pose recognized with data
detection_started     - Detection session started
no_person_detected    - No person in frame
error                 - Error occurred
```

## 🎨 User Interface Sections

### Home Page
- Feature showcase
- Supported poses gallery
- Quick start button

### Live Session
- Real-time video feed
- Confidence and accuracy metrics
- Joint angle measurements
- Real-time feedback panel
- Session controls

### Session History
- Browse past sessions
- Filter by time period
- View performance metrics
- Download session data

### About Section
- Technology stack information
- Feature list
- How it works explanation
- Process flow diagram

## 🔧 Configuration

### Camera Settings

In `session.js`, adjust camera resolution:
```javascript
video: {
    facingMode: 'user',
    width: { ideal: 1280 },     // Adjust resolution
    height: { ideal: 720 }
}
```

### Frame Capture Rate

In `session.js`, adjust FPS:
```javascript
setTimeout(captureFrame, 33);   // ~30 FPS, change for slower/faster
```

### Server Port

In `app.py`, change port:
```python
socketio.run(app, port=5000)  # Change 5000 to desired port
```

## 📊 Performance Tips

1. **Use good lighting** for better pose detection
2. **Keep stable distance** from camera (3-6 feet recommended)
3. **Full body visibility** for accurate angle calculations
4. **Stable internet connection** for real-time processing

## 🐛 Troubleshooting

### Camera Not Working
- Check browser permissions
- Reload page
- Try different browser
- Ensure camera is not in use elsewhere

### No Pose Detected
- Improve lighting
- Move closer to camera
- Ensure full body is visible
- Check pose is in supported list

### High Latency
- Reduce video resolution
- Slow down capture rate
- Check internet connection
- Close other applications

## 🎓 Technical Stack

- **Backend**: Flask 3.0, Python-socketio 5.10
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Computer Vision**: MediaPipe 0.10, OpenCV 4.9
- **Machine Learning**: TensorFlow 2.15, LSTM model
- **Data Processing**: NumPy, Pandas, scikit-learn

## 📈 Future Enhancements

- [ ] Multiple pose simultaneous detection
- [ ] Custom pose training
- [ ] Pose sequence recognition (flows)
- [ ] Audio feedback
- [ ] Export to video with overlays
- [ ] Mobile app version
- [ ] Advanced analytics dashboard
- [ ] Social sharing features

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- MediaPipe for skeleton detection
- TensorFlow for machine learning
- OpenCV for computer vision
- Flask community for excellent framework

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

Built with ❤️ for yoga enthusiasts and AI practitioners
