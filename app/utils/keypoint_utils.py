import numpy as np
from typing import List, Dict, Tuple
from app.models.pose import Keypoint
from app.utils.geometry import calculate_center_point, calculate_scale


# MediaPipe landmark indices
LANDMARK_INDICES = {
    "nose": 0,
    "left_eye_inner": 1,
    "left_eye": 2,
    "left_eye_outer": 3,
    "right_eye_inner": 4,
    "right_eye": 5,
    "right_eye_outer": 6,
    "left_ear": 7,
    "right_ear": 8,
    "mouth_left": 9,
    "mouth_right": 10,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_pinky": 17,
    "right_pinky": 18,
    "left_index": 19,
    "right_index": 20,
    "left_thumb": 21,
    "right_thumb": 22,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_foot_index": 31,
    "right_foot_index": 32
}


def normalize_keypoints(keypoints: List[Keypoint]) -> List[Keypoint]:
    """
    Normalize keypoints to be scale and translation invariant
    
    Strategy:
    1. Center at hip midpoint
    2. Scale by shoulder-hip distance
    
    Args:
        keypoints: List of keypoints to normalize
        
    Returns:
        Normalized keypoints
    """
    if len(keypoints) < 33:
        return keypoints
    
    # Calculate hip center
    hip_center_x, hip_center_y = calculate_center_point(keypoints, [23, 24])
    
    # Calculate scale (distance from shoulders to hips)
    left_shoulder = keypoints[11]
    right_shoulder = keypoints[12]
    shoulder_width = np.sqrt((right_shoulder.x - left_shoulder.x)**2 + 
                            (right_shoulder.y - left_shoulder.y)**2)
    
    # Avoid division by zero
    if shoulder_width < 0.01:
        shoulder_width = 0.1
    
    # Normalize each keypoint
    normalized = []
    for kp in keypoints:
        normalized_kp = Keypoint(
            landmark_id=kp.landmark_id,
            name=kp.name,
            x=(kp.x - hip_center_x) / shoulder_width,
            y=(kp.y - hip_center_y) / shoulder_width,
            z=kp.z / shoulder_width,
            visibility=kp.visibility
        )
        normalized.append(normalized_kp)
    
    return normalized


def get_keypoint_by_name(keypoints: List[Keypoint], name: str) -> Keypoint:
    """Get keypoint by landmark name"""
    landmark_id = LANDMARK_INDICES.get(name)
    if landmark_id is None:
        raise ValueError(f"Unknown landmark name: {name}")
    
    if landmark_id < len(keypoints):
        return keypoints[landmark_id]
    
    raise ValueError(f"Keypoint index {landmark_id} out of range")


def get_keypoint_by_id(keypoints: List[Keypoint], landmark_id: int) -> Keypoint:
    """Get keypoint by landmark ID"""
    if landmark_id < len(keypoints):
        return keypoints[landmark_id]
    
    raise ValueError(f"Keypoint index {landmark_id} out of range")


def filter_low_confidence_keypoints(keypoints: List[Keypoint], threshold: float = 0.5) -> List[Keypoint]:
    """
    Filter out keypoints with low visibility scores
    
    Args:
        keypoints: List of keypoints
        threshold: Minimum visibility threshold (0-1)
        
    Returns:
        Filtered keypoints (low confidence points set to default)
    """
    filtered = []
    for kp in keypoints:
        if kp.visibility < threshold:
            # Create default keypoint for low confidence
            filtered.append(Keypoint(
                landmark_id=kp.landmark_id,
                name=kp.name,
                x=0.5,
                y=0.5,
                z=0.0,
                visibility=0.0
            ))
        else:
            filtered.append(kp)
    
    return filtered


def keypoints_to_array(keypoints: List[Keypoint]) -> np.ndarray:
    """Convert keypoints to numpy array (N x 4: x, y, z, visibility)"""
    return np.array([[kp.x, kp.y, kp.z, kp.visibility] for kp in keypoints])


def array_to_keypoints(array: np.ndarray) -> List[Keypoint]:
    """Convert numpy array to keypoints"""
    keypoints = []
    for i, row in enumerate(array):
        keypoints.append(Keypoint(
            landmark_id=i,
            x=float(row[0]),
            y=float(row[1]),
            z=float(row[2]),
            visibility=float(row[3]) if len(row) > 3 else 1.0
        ))
    return keypoints


def calculate_pose_center(keypoints: List[Keypoint]) -> Tuple[float, float]:
    """Calculate center of pose (average of all keypoints)"""
    x_coords = [kp.x for kp in keypoints if kp.visibility > 0.5]
    y_coords = [kp.y for kp in keypoints if kp.visibility > 0.5]
    
    if not x_coords or not y_coords:
        return 0.5, 0.5
    
    return np.mean(x_coords), np.mean(y_coords)
