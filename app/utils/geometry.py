import numpy as np
from typing import Tuple, List
from app.models.pose import Keypoint


def calculate_angle(point1: Keypoint, point2: Keypoint, point3: Keypoint) -> float:
    """
    Calculate angle at point2 formed by point1-point2-point3
    
    Args:
        point1: First point
        point2: Vertex point
        point3: Third point
        
    Returns:
        Angle in degrees (0-180)
    """
    # Create vectors
    vector1 = np.array([point1.x - point2.x, point1.y - point2.y])
    vector2 = np.array([point3.x - point2.x, point3.y - point2.y])
    
    # Calculate angle using dot product
    cos_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-6)
    
    # Clip to avoid numerical errors
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    angle = np.arccos(cos_angle)
    return np.degrees(angle)


def euclidean_distance(point1: Keypoint, point2: Keypoint) -> float:
    """Calculate Euclidean distance between two keypoints"""
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def calculate_distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate 2D Euclidean distance"""
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """Calculate 3D Euclidean distance"""
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-180 range"""
    while angle > 180:
        angle -= 360
    while angle < 0:
        angle += 360
    if angle > 180:
        angle = 360 - angle
    return angle


def calculate_center_point(keypoints: List[Keypoint], indices: List[int]) -> Tuple[float, float]:
    """
    Calculate center point of specified keypoints
    
    Args:
        keypoints: List of keypoints
        indices: Indices of keypoints to average
        
    Returns:
        (x, y) coordinates of center point
    """
    x_coords = [keypoints[i].x for i in indices if i < len(keypoints)]
    y_coords = [keypoints[i].y for i in indices if i < len(keypoints)]
    
    if not x_coords or not y_coords:
        return 0.5, 0.5
    
    return np.mean(x_coords), np.mean(y_coords)


def calculate_bounding_box(keypoints: List[Keypoint]) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box of all keypoints
    
    Returns:
        (min_x, min_y, max_x, max_y)
    """
    x_coords = [kp.x for kp in keypoints]
    y_coords = [kp.y for kp in keypoints]
    
    return min(x_coords), min(y_coords), max(x_coords), max(y_coords)


def calculate_scale(keypoints: List[Keypoint]) -> float:
    """
    Calculate scale based on bounding box diagonal
    Used for normalization
    """
    min_x, min_y, max_x, max_y = calculate_bounding_box(keypoints)
    width = max_x - min_x
    height = max_y - min_y
    
    return np.sqrt(width**2 + height**2)
