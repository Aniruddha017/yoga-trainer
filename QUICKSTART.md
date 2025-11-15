# Quick Start Guide

## ✅ Installation Complete!

All required packages have been installed successfully.

## 🚀 How to Run

### 1. Start the Backend Server

```powershell
# Make sure you're in the project directory
cd "d:\yoga_webapp\new yoga app"

# Activate virtual environment
.\myenv\Scripts\activate

# Start the FastAPI server
python app/main.py
```

Or use uvicorn directly:
```powershell
uvicorn app.main:app --reload
```

### 2. Access the Application

- **Frontend**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## 📋 API Endpoints Created

### Pose Detection
- `POST /api/v1/pose-detection/detect-pose` - Detect pose from camera image
- `GET /api/v1/pose-detection/health` - Health check

### Accuracy Calculation
- `POST /api/v1/accuracy/calculate-accuracy` - Compare user pose with reference
- `GET /api/v1/accuracy/health` - Health check

### Reference Poses
- `GET /api/v1/reference/poses` - List all reference poses
- `GET /api/v1/reference/poses/{pose_id}` - Get specific reference pose
- `POST /api/v1/reference/poses/upload` - Upload new reference pose
- `GET /api/v1/reference/health` - Health check

## 📁 What Was Created

### Backend (FastAPI)
- ✅ `app/main.py` - FastAPI application
- ✅ `app/config.py` - Configuration settings
- ✅ `app/models/pose.py` - Pydantic data models
- ✅ `app/models/schemas.py` - Request/response schemas
- ✅ `app/services/pose_detector.py` - MediaPipe integration
- ✅ `app/services/accuracy_calculator.py` - Accuracy calculation logic
- ✅ `app/utils/geometry.py` - Angle calculations
- ✅ `app/utils/keypoint_utils.py` - Keypoint normalization
- ✅ `app/api/routes/pose_detection.py` - Pose detection endpoints
- ✅ `app/api/routes/accuracy.py` - Accuracy endpoints
- ✅ `app/api/routes/reference.py` - Reference pose endpoints

### Frontend (HTML/CSS/JS)
- ✅ `frontend/index.html` - Main webpage
- ✅ `frontend/css/styles.css` - Responsive styling
- ✅ `frontend/js/api_client.js` - API communication
- ✅ `frontend/js/camera.js` - Webcam management
- ✅ `frontend/js/pose_overlay.js` - Pose visualization
- ✅ `frontend/js/main.js` - Main application logic

### Project Structure
- ✅ `requirements.txt` - All dependencies
- ✅ `README.md` - Complete documentation
- ✅ `.gitignore` - Git ignore rules
- ✅ `data/reference_poses/` - Reference pose storage
- ✅ `data/uploads/` - Temporary uploads folder

## 🧘 Next Steps

### 1. Add Reference Poses

You have 82 yoga images. You need to either:

**Option A: Use MediaPipe to process them automatically**
```python
# Create a script: scripts/process_reference_images.py
from app.services.pose_detector import get_pose_detector
import json
import base64
from pathlib import Path

detector = get_pose_detector()

# Process each image
for image_file in Path("path/to/your/82/images").glob("*.jpg"):
    pose = detector.detect_pose_from_file(str(image_file))
    if pose:
        pose_data = {
            "pose_id": image_file.stem,
            "name": image_file.stem.replace("_", " ").title(),
            "difficulty": "beginner",
            "view_angle": "front",
            "keypoints": [kp.dict() for kp in pose.keypoints],
            "reference_image": f"data/reference_poses/images/{image_file.name}",
            "description": ""
        }
        
        # Save keypoints
        output_file = Path(f"data/reference_poses/keypoints/{image_file.stem}.json")
        output_file.write_text(json.dumps(pose_data, indent=2))
        
        # Copy image
        import shutil
        shutil.copy(image_file, f"data/reference_poses/images/{image_file.name}")
```

**Option B: Upload via the web interface**
1. Start the server
2. Use the upload endpoint at http://localhost:8000/docs
3. Upload each image one by one

### 2. Test the Application

1. Start the server: `python app/main.py`
2. Open browser: http://localhost:8000
3. Allow camera permissions
4. Select a yoga pose from dropdown
5. Click "Start Camera"
6. Position yourself and click "Check Pose"
7. See your accuracy results!

## 🔧 Configuration

Edit `app/config.py` to customize:

```python
# MediaPipe settings
mediapipe_model_complexity: int = 1  # 0 (fast), 1 (balanced), 2 (accurate)
mediapipe_min_detection_confidence: float = 0.5
mediapipe_min_tracking_confidence: float = 0.5

# Accuracy calculation weights
angle_weight: float = 0.6  # 60% weight on joint angles
distance_weight: float = 0.4  # 40% weight on spatial distance
angle_penalty_factor: float = 0.5  # Penalty per degree difference
```

## 🐛 Troubleshooting

### Camera Not Working
- Ensure camera permissions are granted in browser
- Use Chrome, Firefox, or Edge (not IE)
- HTTPS required in production (localhost works with HTTP)

### No Reference Poses Found
- Add your 82 yoga images to `data/reference_poses/`
- Process them using the script above or upload via API

### Import Errors
```powershell
# Reinstall packages
pip install -r requirements.txt
```

### Port Already in Use
```powershell
# Change port in app/main.py or use:
uvicorn app.main:app --port 8080
```

## 📊 How It Works

1. **User captures pose** via webcam
2. **MediaPipe detects** 33 body landmarks
3. **Accuracy calculator compares** user keypoints vs reference
4. **Joint angles** (60% weight) and **spatial distances** (40% weight) are calculated
5. **Results displayed** with color-coded feedback:
   - 🟢 Green (90-100%): Excellent
   - 🟡 Yellow (75-89%): Good  
   - 🟠 Orange (50-74%): Needs adjustment
   - 🔴 Red (<50%): Incorrect

## 🎯 Features Available

✅ Real-time pose detection from webcam
✅ Accuracy calculation with joint-by-joint feedback
✅ Color-coded pose visualization
✅ Reference pose management
✅ Responsive web interface
✅ RESTful API with Swagger docs
✅ Front-view pose support (as discussed)

## 📝 Testing the API

### Example: Detect Pose
```bash
curl -X POST "http://localhost:8000/api/v1/pose-detection/detect-pose" \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,/9j/4AAQ..."}'
```

### Example: List Reference Poses
```bash
curl "http://localhost:8000/api/v1/reference/poses"
```

## 🔜 Future Enhancements

- [ ] Add manual keypoint annotation tool (as you mentioned)
- [ ] Process your 82 yoga images
- [ ] Add side-view support later
- [ ] Real-time streaming with WebSockets
- [ ] User authentication
- [ ] Progress tracking
- [ ] Mobile app

---

**You're all set!** Run `python app/main.py` to start testing! 🎉
