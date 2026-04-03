# 🚀 Quick Start Guide - Yoga Pose Estimator Web App

## System Requirements
- Python 3.8 or higher
- Webcam
- Modern web browser
- 4GB RAM minimum
- Windows, macOS, or Linux

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/AV031/Yoga_Pose_Correction.git
cd Yoga_Pose_Correction
```

### 2. Create Virtual Environment (Optional but Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask and Flask-CORS
- TensorFlow and Keras
- MediaPipe
- OpenCV
- NumPy, Pandas, scikit-learn
- Socket.io for real-time communication

### 4. Run the Application
```bash
python app.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    YOGA POSE ESTIMATOR - WEB APPLICATION                     ║
║                                                              ║
║    Starting Flask server...                                  ║
║    Open http://localhost:5000 in your browser               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### 5. Open in Browser
Navigate to: **http://localhost:5000**

## First Time Setup

### Model Initialization
When you first run the application:
1. The LSTM model will be loaded (takes ~10-15 seconds)
2. MediaPipe will initialize pose detection
3. You'll see a "Connecting..." indicator in the top-right

### Camera Permissions
1. When starting your first session, you'll be prompted to allow camera access
2. Click "Allow" to give the browser permission
3. If denied, you can enable it in browser settings

## Usage Workflow

```
1. HOME PAGE
   ├─ Learn about features
   └─ Browse supported poses

2. START LIVE SESSION
   ├─ Click "Start Capture"
   ├─ Stand in front of camera
   └─ System detects pose in real-time

3. VIEW FEEDBACK
   ├─ See detected pose name
   ├─ Check accuracy percentage
   ├─ Read joint angle measurements
   └─ Get correction tips

4. END SESSION
   ├─ Click "End Session"
   ├─ View summary statistics
   └─ Click "Save Session" to download

5. CHECK HISTORY
   ├─ Go to History tab
   ├─ Filter by time period
   └─ Review past sessions
```

## Features Walkthrough

### 🎯 Real-Time Detection
- Detects 33 body landmarks using MediaPipe
- Processes video at ~30 FPS
- Displays pose confidence score
- Shows accuracy against reference poses

### 📊 Live Metrics
- **Shoulder Angle**: Degrees between shoulder and elbow
- **Elbow Angle**: Joint angle measurement
- **Knee Angle**: Lower body joint angle
- **Stability Score**: How stable your pose is (0-100%)

### 💡 Smart Feedback
- Real-time correction suggestions
- Body part specific tips
- Improvement recommendations
- Pose-specific guidance

### 📈 Progress Tracking
- Session duration tracking
- Frame-by-frame analysis
- Accuracy history
- Personal best records

## Common Issues & Solutions

### ❌ "Camera access denied"
**Solution:**
- Check browser camera permissions
- Go to Settings → Site settings → Camera
- Allow camera for localhost
- Reload the page

### ❌ "No pose detected" (black frame)
**Solution:**
- Ensure good lighting
- Move closer to camera (3-6 feet)
- Make sure full body is visible
- Check that you're not against a wall

### ❌ "Connection error"
**Solution:**
- Check if Flask server is running
- Verify browser console for errors
- Restart the application
- Clear browser cache

### ❌ High CPU usage
**Solution:**
- Reduce camera resolution in code
- Decrease frame capture rate
- Close other applications
- Update graphics drivers

### ❌ Slow detection
**Solution:**
- Improve internet connection
- Move camera closer
- Improve lighting conditions
- Reduce video resolution

## Tips for Best Results

### 📹 Camera Setup
- **Distance**: 3-6 feet from camera
- **Angle**: Slightly below head level
- **Lighting**: Good natural or artificial light
- **Background**: Solid, non-reflective background

### 🧘 Pose Tips
- Hold poses steady for 2-3 seconds
- Full body visibility required
- Move slowly to camera sees transitions
- Maintain good posture

### 🔧 Performance Tips
- Use Chrome or Firefox for best experience
- Close unnecessary applications
- Use wired internet if possible
- Keep room well-lit

## Advanced Configuration

### Change Server Port
Edit `app.py`:
```python
socketio.run(app, port=8000)  # Change 5000 to your port
```

### Adjust Camera Resolution
Edit `static/js/session.js`:
```javascript
video: {
    width: { ideal: 640 },    // Lower for faster processing
    height: { ideal: 480 }
}
```

### Change Detection Speed
Edit `static/js/session.js`:
```javascript
setTimeout(captureFrame, 50);  // Higher number = slower
```

## File Structure
```
Yoga_Pose_Correction/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── WEB_APP_README.md        # Web app documentation
├── QUICKSTART.md            # This file
├── templates/
│   └── index.html           # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css        # Application styling
│   └── js/
│       ├── main.js          # Main JavaScript logic
│       └── session.js       # Session management
├── pose_detector.py         # Pose detection module
├── pose_analyzer.py         # Pose analysis module
├── lstm_model.py            # LSTM classification
├── reference_poses.py       # Reference pose data
└── session_data/            # Saved sessions (auto-created)
```

## Next Steps

### 🎓 Learning
1. Read [WEB_APP_README.md](WEB_APP_README.md) for full documentation
2. Explore the about page for technical details
3. Review GitHub repository for updates

### 🔧 Customization
1. Train custom poses with `train_model.py`
2. Add new yoga poses to `reference_poses.py`
3. Modify UI styling in `static/css/style.css`
4. Extend backend API in `app.py`

### 🚀 Deployment
1. Use gunicorn for production
2. Deploy to Heroku, AWS, or similar
3. Set up proper HTTPS
4. Configure CORS settings

## Getting Help

### Resources
- Check GitHub Issues for common problems
- Review application logs for errors
- Check browser console (F12) for JavaScript errors

### Error Reporting
Include:
1. Operating system
2. Browser type and version
3. Python version
4. Error message/screenshot
5. Steps to reproduce

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Q` | Quit application |
| `S` | Save session |
| `P` | Pause detection |
| `R` | Reset session |

## Performance Benchmarks

| Component | Requirement |
|-----------|------------|
| CPU | 20-40% usage (average) |
| Memory | 300-500MB |
| GPU | Optional (2GB+ for acceleration) |
| Bandwidth | 1-5 Mbps |
| FPS | 25-30 FPS |

## Video Tutorial

[Watch full tutorial on YouTube](https://youtube.com)

---

**Happy yoga practicing! 🧘‍♂️**

For detailed features and API documentation, see [WEB_APP_README.md](WEB_APP_README.md)
