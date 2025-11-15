# Yoga Pose Accuracy Measurement WebApp

A FastAPI-based web application that uses computer vision (MediaPipe) to measure the accuracy of yoga poses by comparing user poses from webcam input against reference images.

## Features

- 🧘 Real-time pose detection using MediaPipe
- 📊 Accuracy calculation with joint angle and position analysis
- 🎯 Joint-by-joint feedback with color-coded visualization
- 📸 Webcam integration for live pose capture
- 🖼️ Reference pose management (upload and compare)
- 📱 Responsive web interface

## Project Structure

```
d:\yoga_webapp\new yoga app\
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Application configuration
│   ├── api/
│   │   └── routes/
│   │       ├── pose_detection.py   # POST /api/v1/pose-detection/detect-pose
│   │       ├── accuracy.py         # POST /api/v1/accuracy/calculate-accuracy
│   │       └── reference.py        # GET /api/v1/reference/poses
│   ├── models/
│   │   ├── pose.py                 # Pydantic models for poses
│   │   └── schemas.py              # Request/response schemas
│   ├── services/
│   │   ├── pose_detector.py        # MediaPipe pose detection
│   │   └── accuracy_calculator.py  # Accuracy calculation logic
│   └── utils/
│       ├── geometry.py             # Angle calculations
│       └── keypoint_utils.py       # Keypoint normalization
├── data/
│   └── reference_poses/
│       ├── images/                 # Reference yoga pose images
│       └── keypoints/              # Reference keypoint JSON files
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── api_client.js
│       ├── camera.js
│       ├── pose_overlay.js
│       └── main.js
├── requirements.txt
└── README.md
```

## Installation

### 1. Install Dependencies

```powershell
# Activate virtual environment
.\myenv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Required Packages

- FastAPI (0.104.1)
- Uvicorn (0.24.0)
- MediaPipe (0.10.8)
- OpenCV-Python (4.8.1.78)
- NumPy (1.24.3)
- Pillow (10.1.0)
- Pydantic (2.5.0)
- SciPy (1.11.4)

## Usage

### Start the Server

```powershell
# Run the FastAPI server
python -m uvicorn app.main:app --reload
```

Or run directly:

```powershell
python app/main.py
```

The application will be available at:
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### API Endpoints

#### 1. Detect Pose
```
POST /api/v1/pose-detection/detect-pose
Content-Type: application/json

{
  "image": "base64_encoded_image_string"
}
```

#### 2. Calculate Accuracy
```
POST /api/v1/accuracy/calculate-accuracy
Content-Type: application/json

{
  "user_keypoints": [...],
  "reference_pose_id": "warrior_pose"
}
```

#### 3. List Reference Poses
```
GET /api/v1/reference/poses
```

#### 4. Get Specific Reference Pose
```
GET /api/v1/reference/poses/{pose_id}
```

#### 5. Upload Reference Pose
```
POST /api/v1/reference/poses/upload
Content-Type: application/json

{
  "pose_id": "new_pose",
  "name": "New Yoga Pose",
  "image": "base64_encoded_image",
  "difficulty": "beginner",
  "description": "Pose instructions..."
}
```

## How It Works

### 1. Pose Detection
- Uses MediaPipe Pose to detect 33 body landmarks from images
- Extracts keypoint coordinates (x, y, z) and visibility scores
- Validates detection confidence before processing

### 2. Accuracy Calculation
The accuracy score is calculated using a weighted algorithm:

**Formula**: `Accuracy = (0.6 × Angle Score) + (0.4 × Distance Score)`

- **Angle Score (60%)**: Compares joint angles at major joints (elbows, knees, hips, shoulders)
- **Distance Score (40%)**: Measures normalized spatial similarity between keypoints

### 3. Normalization
- Centers pose at hip midpoint
- Scales by shoulder width for size invariance
- Ensures fair comparison regardless of distance from camera

### 4. Feedback Generation
- **Overall Accuracy**: 0-100% score
- **Joint-by-Joint Analysis**: Individual scores for each joint
- **Color Coding**:
  - 🟢 Green (90-100%): Excellent
  - 🟡 Yellow (75-89%): Good
  - 🟠 Orange (50-74%): Needs adjustment
  - 🔴 Red (<50%): Incorrect

## Adding Reference Poses

### Option 1: Upload via API
Use the frontend or API to upload a new reference pose with an image.

### Option 2: Manual JSON Creation
1. Place yoga pose image in `data/reference_poses/images/`
2. Create JSON file in `data/reference_poses/keypoints/`:

```json
{
  "pose_id": "warrior_pose",
  "name": "Warrior Pose (Virabhadrasana I)",
  "difficulty": "beginner",
  "view_angle": "front",
  "keypoints": [
    {"landmark_id": 0, "name": "nose", "x": 0.5, "y": 0.2, "z": 0.0, "visibility": 0.98},
    ...
  ],
  "reference_image": "data/reference_poses/images/warrior_pose.jpg",
  "description": "Stand with feet apart, arms raised overhead..."
}
```

## Configuration

Edit `app/config.py` to customize:

```python
# MediaPipe settings
mediapipe_model_complexity: int = 1  # 0, 1, or 2
mediapipe_min_detection_confidence: float = 0.5
mediapipe_min_tracking_confidence: float = 0.5

# Accuracy calculation weights
angle_weight: float = 0.6
distance_weight: float = 0.4
angle_penalty_factor: float = 0.5
```

## Development

### Running Tests
```powershell
# Add tests in tests/ directory
pytest
```

### Code Structure
- **Models**: Pydantic models for data validation
- **Services**: Business logic (pose detection, accuracy calculation)
- **Routes**: API endpoint handlers
- **Utils**: Helper functions (geometry, keypoint manipulation)

## Browser Requirements

- Modern browser with WebRTC support (Chrome, Firefox, Edge)
- Camera permissions enabled
- HTTPS for production deployment (WebRTC requirement)

## Troubleshooting

### Camera Not Working
- Ensure camera permissions are granted
- Check if another application is using the camera
- Use HTTPS in production (localhost works with HTTP)

### Low Detection Confidence
- Ensure good lighting
- Stand in front of a plain background
- Ensure full body is visible in camera frame
- Maintain proper distance from camera

### Import Errors
- Ensure all packages are installed: `pip install -r requirements.txt`
- Activate virtual environment: `.\myenv\Scripts\activate`

## Future Enhancements

- [ ] Add side view and multi-angle pose detection
- [ ] Implement real-time streaming with WebSockets
- [ ] Add pose sequence tracking (yoga flow)
- [ ] User authentication and progress tracking
- [ ] Mobile app development
- [ ] Advanced pose analytics and reports

## License

This project is for educational and personal use.

## Credits

- **MediaPipe**: Google's pose detection solution
- **FastAPI**: Modern Python web framework
- **OpenCV**: Computer vision library
