import mediapipe as mp
import cv2
import numpy as np
import base64
from typing import Optional, Tuple
from io import BytesIO
from PIL import Image

from app.models.pose import Keypoint, Pose
from app.config import settings


class PoseDetector:
    """MediaPipe-based pose detection service"""
    
    def __init__(self):
        """Initialize MediaPipe Pose"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=settings.mediapipe_model_complexity,
            min_detection_confidence=settings.mediapipe_min_detection_confidence,
            min_tracking_confidence=settings.mediapipe_min_tracking_confidence
        )
        
        # Landmark names mapping
        self.landmark_names = [
            "nose", "left_eye_inner", "left_eye", "left_eye_outer",
            "right_eye_inner", "right_eye", "right_eye_outer",
            "left_ear", "right_ear", "mouth_left", "mouth_right",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_pinky", "right_pinky",
            "left_index", "right_index", "left_thumb", "right_thumb",
            "left_hip", "right_hip", "left_knee", "right_knee",
            "left_ankle", "right_ankle", "left_heel", "right_heel",
            "left_foot_index", "right_foot_index"
        ]
    
    def decode_base64_image(self, base64_string: str) -> np.ndarray:
        """
        Decode base64 image string to numpy array
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            Image as numpy array (BGR format for OpenCV)
        """
        # Remove header if present
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB numpy array
        image_np = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_np
        
        return image_bgr
    
    def detect_pose(self, image: np.ndarray) -> Optional[Pose]:
        """
        Detect pose from image
        
        Args:
            image: Image as numpy array (BGR format)
            
        Returns:
            Pose object with keypoints or None if detection fails
        """
        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
        
        # Extract keypoints
        keypoints = []
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            # Clamp values to [0, 1] range to handle floating-point precision issues
            keypoint = Keypoint(
                landmark_id=i,
                name=self.landmark_names[i] if i < len(self.landmark_names) else f"landmark_{i}",
                x=max(0.0, min(1.0, landmark.x)),
                y=max(0.0, min(1.0, landmark.y)),
                z=landmark.z,  # z can be outside [0, 1] range
                visibility=max(0.0, min(1.0, landmark.visibility))
            )
            keypoints.append(keypoint)
        
        # Calculate overall confidence (average visibility of key landmarks)
        key_landmarks = [11, 12, 23, 24]  # Shoulders and hips
        confidence = np.mean([keypoints[i].visibility for i in key_landmarks if i < len(keypoints)])
        
        return Pose(keypoints=keypoints, confidence=float(confidence))
    
    def detect_pose_from_base64(self, base64_string: str) -> Optional[Pose]:
        """
        Detect pose from base64 encoded image
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            Pose object or None
        """
        try:
            image = self.decode_base64_image(base64_string)
            return self.detect_pose(image)
        except Exception as e:
            print(f"Error detecting pose from base64: {e}")
            return None
    
    def detect_pose_from_file(self, file_path: str) -> Optional[Pose]:
        """
        Detect pose from image file
        
        Args:
            file_path: Path to image file
            
        Returns:
            Pose object or None
        """
        try:
            image = cv2.imread(file_path)
            if image is None:
                return None
            return self.detect_pose(image)
        except Exception as e:
            print(f"Error detecting pose from file: {e}")
            return None
    
    def __del__(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, 'pose'):
            self.pose.close()


# Singleton instance
_pose_detector_instance: Optional[PoseDetector] = None


def get_pose_detector() -> PoseDetector:
    """Get singleton pose detector instance"""
    global _pose_detector_instance
    if _pose_detector_instance is None:
        _pose_detector_instance = PoseDetector()
    return _pose_detector_instance
