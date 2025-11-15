# Plan: Yoga Pose Accuracy Measurement WebApp

Build a FastAPI-based webapp that uses computer vision (MediaPipe) to compare user yoga poses from webcam input against 82 reference images, calculating accuracy through keypoint detection and multi-metric analysis.

## Steps

1. **Set up project structure and dependencies** - Create `app/main.py`, `requirements.txt` with FastAPI, MediaPipe, OpenCV, and organize folders for `app/`, `data/`, `frontend/`, `tests/`

2. **Build pose detection service** - Implement `app/services/pose_detector.py` using MediaPipe to extract 33 body landmarks from images, with confidence validation

3. **Process reference dataset** - Create script to extract and store keypoints from your 82 yoga images as JSON in `data/reference_poses/`, including normalized coordinates and metadata

4. **Implement accuracy calculation** - Build `app/services/accuracy_calculator.py` comparing joint angles and normalized keypoint distances between user and reference poses (weighted scoring: 60% angles, 40% distance)

5. **Create FastAPI endpoints** - Add routes in `app/api/routes/` for pose detection (POST `/api/v1/detect-pose`), accuracy calculation (POST `/api/v1/calculate-accuracy`), and listing reference poses (GET `/api/v1/reference-poses`)

6. **Develop frontend interface** - Build `frontend/index.html` with WebRTC camera access, Canvas overlay for pose landmarks, exercise selector dropdown, and real-time accuracy display with per-joint feedback

## Further Considerations

1. **Camera view handling** - Will poses require front view, side view, or both? Consider multi-angle detection or per-pose camera angle specifications

2. **Accuracy threshold calibration** - Start with weighted scoring (60% joint angles, 40% spatial distance) then adjust based on testing; consider difficulty levels per pose

3. **Real-time performance** - Process at 10-15 FPS initially; upgrade to WebSocket streaming or client-side TensorFlow.js if latency becomes an issue

## Recommended Architecture

### Project Structure
```
d:\yoga_webapp\new yoga app\
├── myenv/                          # (existing virtual environment)
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── pose_detection.py   # Pose detection endpoints
│   │   │   ├── accuracy.py         # Accuracy calculation endpoints
│   │   │   └── reference.py        # Reference pose management
│   │   └── dependencies.py         # Shared dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pose.py                 # Pydantic models for poses
│   │   └── schemas.py              # Request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pose_detector.py        # MediaPipe pose detection logic
│   │   ├── accuracy_calculator.py  # Pose comparison & accuracy scoring
│   │   └── image_processor.py      # Image preprocessing utilities
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── keypoint_utils.py       # Keypoint manipulation functions
│   │   └── geometry.py             # Angle/distance calculations
│   └── config.py                   # Application configuration
├── data/
│   ├── reference_poses/            # Reference yoga pose images/keypoints
│   │   ├── warrior_pose.json
│   │   ├── tree_pose.json
│   │   └── ...
│   └── uploads/                    # Temporary user uploads
├── frontend/
│   ├── index.html                  # Main web interface
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── camera.js               # Camera access & capture
│   │   ├── pose_overlay.js         # Draw pose landmarks on canvas
│   │   └── api_client.js           # FastAPI communication
│   └── assets/
├── tests/
│   ├── __init__.py
│   ├── test_pose_detection.py
│   └── test_accuracy.py
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── .gitignore
└── README.md
```

## Key Technologies & Libraries

### Backend (Python/FastAPI)
```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6          # File upload support

# Computer Vision & Pose Detection
mediapipe==0.10.8                # Google's pose estimation library
opencv-python==4.8.1.78          # Image processing
numpy==1.24.3                    # Numerical operations
Pillow==10.1.0                   # Image manipulation

# Data Validation & Serialization
pydantic==2.5.0
pydantic-settings==2.1.0

# Utilities
python-dotenv==1.0.0             # Environment variable management
scipy==1.11.4                    # Scientific computing for advanced geometry
```

### Frontend
- **HTML5** - Web structure
- **CSS3** - Styling with Flexbox/Grid
- **JavaScript (Vanilla or React)** - Core logic
- **WebRTC API** - Camera access via `navigator.mediaDevices.getUserMedia()`
- **Canvas API** - Real-time pose landmark rendering
- **Fetch API** - HTTP requests to FastAPI backend

## Pose Detection Approach

### MediaPipe Pose
- Pre-trained model with 33 body landmarks (shoulders, hips, knees, ankles, etc.)
- Real-time performance (60+ FPS on CPU)
- Cross-platform support
- Excellent for yoga poses with full-body tracking

**MediaPipe Landmarks:**
```
0: Nose, 11-12: Shoulders, 13-14: Elbows, 15-16: Wrists
23-24: Hips, 25-26: Knees, 27-28: Ankles, etc.
```

## Pose Accuracy Calculation Algorithm

### Multi-Metric Comparison

**1. Joint Angle Similarity (Primary - 60%)**
- Calculate angles at major joints (elbows, knees, hips, shoulders)
- Compare reference vs. user angles
- Formula: `angle_score = max(0, 100 - angle_diff * penalty_factor)`

**2. Normalized Distance Matching (Secondary - 40%)**
- Normalize keypoints to scale-invariant coordinates
- Calculate Euclidean distance between corresponding landmarks
- Formula: `distance_score = 100 * exp(-sum(euclidean_distances) / threshold)`

**3. Weighted Scoring System:**
```python
final_accuracy = (
    0.60 * joint_angle_score +
    0.40 * normalized_distance_score
)
```

### Implementation Pseudocode
```python
def calculate_pose_accuracy(reference_keypoints, user_keypoints):
    # 1. Normalize both poses (scale, translate to origin)
    ref_norm = normalize_keypoints(reference_keypoints)
    user_norm = normalize_keypoints(user_keypoints)
    
    # 2. Calculate joint angles
    ref_angles = calculate_joint_angles(ref_norm)
    user_angles = calculate_joint_angles(user_norm)
    
    # 3. Compute angle differences
    angle_score = compute_angle_similarity(ref_angles, user_angles)
    
    # 4. Compute spatial distance
    distance_score = compute_distance_similarity(ref_norm, user_norm)
    
    # 5. Weighted average
    final_score = 0.6 * angle_score + 0.4 * distance_score
    
    # 6. Generate per-joint feedback
    feedback = generate_joint_feedback(ref_angles, user_angles)
    
    return {
        "overall_accuracy": final_score,
        "joint_feedback": feedback,
        "angle_score": angle_score,
        "distance_score": distance_score
    }
```

## FastAPI Endpoint Design

### Core Endpoints

```python
# 1. Real-time pose detection
POST /api/v1/detect-pose
Body: { "image": "base64_encoded_image" }
Response: { "keypoints": [...], "confidence": 0.95 }

# 2. Calculate accuracy
POST /api/v1/calculate-accuracy
Body: { 
    "user_keypoints": [...],
    "reference_pose_id": "warrior_pose"
}
Response: {
    "overall_accuracy": 87.5,
    "joint_scores": {...},
    "feedback": "Adjust left knee angle"
}

# 3. Get reference poses
GET /api/v1/reference-poses
Response: [
    { "id": "warrior_pose", "name": "Warrior Pose", "thumbnail": "..." },
    ...
]

# 4. Upload custom reference pose
POST /api/v1/reference-poses
Body: { "image": "...", "name": "Custom Pose" }

# 5. WebSocket for real-time streaming (optional)
WS /ws/pose-stream
```

## Frontend Integration Strategy

### Camera Access & Capture
```javascript
// Access user camera
const stream = await navigator.mediaDevices.getUserMedia({ 
    video: { width: 640, height: 480 } 
});
videoElement.srcObject = stream;

// Capture frame from video
const canvas = document.createElement('canvas');
canvas.getContext('2d').drawImage(videoElement, 0, 0);
const imageData = canvas.toDataURL('image/jpeg');

// Send to backend
const response = await fetch('/api/v1/detect-pose', {
    method: 'POST',
    body: JSON.stringify({ image: imageData })
});
```

### Real-time Display
- Draw MediaPipe landmarks on HTML5 Canvas
- Overlay reference pose skeleton
- Color-code joints by accuracy (green=good, yellow=ok, red=adjust)
- Display accuracy percentage prominently

## Dataset Management

### Reference Pose Storage Format
```json
{
  "pose_id": "warrior_pose",
  "name": "Warrior Pose (Virabhadrasana I)",
  "difficulty": "beginner",
  "keypoints": [
    {"landmark_id": 0, "x": 0.5, "y": 0.2, "z": -0.1, "visibility": 0.98},
    ...
  ],
  "reference_image": "data/reference_poses/warrior_pose.jpg",
  "description": "Stand with feet apart, arms raised..."
}
```

## Performance Optimization

### Backend
- Cache MediaPipe model initialization
- Use async endpoints for concurrent processing
- Implement request batching for multiple frames

### Frontend
- Reduce frame rate (10-15 FPS sufficient for yoga)
- Compress images before sending to backend
- Debounce API calls

### Optional: Client-side Processing
- Use TensorFlow.js + PoseNet for in-browser detection
- Only send keypoints to backend (not full images)

## Implementation Steps

1. Install dependencies - Create `requirements.txt` and install packages
2. Set up FastAPI skeleton - Create basic app structure
3. Implement pose detection service - MediaPipe integration
4. Build accuracy calculator - Angle/distance algorithms
5. Create reference pose dataset - Process 82 yoga images
6. Develop frontend - Camera access + display
7. Connect frontend to backend - API integration
8. Test & refine - Adjust accuracy thresholds

## Key Considerations

- **Lighting conditions** - Train/test with varied lighting
- **Camera angles** - Consider front/side view requirements for different poses
- **Confidence thresholds** - Reject low-confidence detections
- **Privacy** - Process images in-memory, don't persist user data
- **Accessibility** - Provide audio feedback for visually impaired users
