from pydantic import BaseModel, Field
from typing import List, Optional


class Keypoint(BaseModel):
    """Single keypoint with coordinates and visibility"""
    landmark_id: int = Field(..., description="MediaPipe landmark ID (0-32)")
    name: Optional[str] = Field(None, description="Landmark name (e.g., 'nose', 'left_shoulder')")
    x: float = Field(..., description="X coordinate (0-1 for raw, can be negative when normalized)")
    y: float = Field(..., description="Y coordinate (0-1 for raw, can be negative when normalized)")
    z: float = Field(..., description="Depth coordinate")
    visibility: float = Field(..., ge=0, le=1, description="Visibility score (0-1)")


class Pose(BaseModel):
    """Complete pose with all keypoints"""
    keypoints: List[Keypoint] = Field(..., description="List of 33 body landmarks")
    confidence: float = Field(..., ge=0, le=1, description="Overall detection confidence")


class ReferencePose(BaseModel):
    """Reference yoga pose with metadata"""
    pose_id: str = Field(..., description="Unique pose identifier")
    base_pose_name: Optional[str] = Field(None, description="Base pose name without view suffix")
    name: str = Field(..., description="Pose name (e.g., 'Warrior Pose')")
    difficulty: str = Field(default="beginner", description="Difficulty level")
    view_angle: str = Field(default="front", description="Camera angle (front/side/back)")
    keypoints: List[Keypoint] = Field(..., description="Reference pose keypoints")
    reference_image: Optional[str] = Field(None, description="Path to reference image")
    thumbnail: Optional[str] = Field(None, description="Base64 thumbnail or URL")
    description: Optional[str] = Field(None, description="Pose instructions")


class JointAngles(BaseModel):
    """Calculated joint angles for a pose"""
    left_elbow: Optional[float] = None
    right_elbow: Optional[float] = None
    left_shoulder: Optional[float] = None
    right_shoulder: Optional[float] = None
    left_hip: Optional[float] = None
    right_hip: Optional[float] = None
    left_knee: Optional[float] = None
    right_knee: Optional[float] = None


class JointFeedback(BaseModel):
    """Feedback for individual joint"""
    joint_name: str
    score: float = Field(..., ge=0, le=100)
    angle_difference: Optional[float] = None
    feedback_message: str


class AccuracyResult(BaseModel):
    """Pose accuracy calculation result"""
    overall_accuracy: float = Field(..., ge=0, le=100, description="Overall accuracy percentage")
    angle_score: float = Field(..., ge=0, le=100, description="Joint angle similarity score")
    distance_score: float = Field(..., ge=0, le=100, description="Keypoint distance similarity score")
    joint_feedback: List[JointFeedback] = Field(default=[], description="Per-joint feedback")
    general_feedback: str = Field(..., description="General improvement suggestions")
