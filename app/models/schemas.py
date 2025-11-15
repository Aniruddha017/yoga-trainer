from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.pose import Keypoint, Pose, AccuracyResult, ReferencePose


# Request Schemas
class DetectPoseRequest(BaseModel):
    """Request to detect pose from image"""
    image: str = Field(..., description="Base64 encoded image")


class CalculateAccuracyRequest(BaseModel):
    """Request to calculate pose accuracy"""
    user_keypoints: List[Keypoint] = Field(..., description="User's detected keypoints")
    reference_pose_id: str = Field(..., description="ID of reference pose to compare against")


class UploadReferencePoseRequest(BaseModel):
    """Request to upload custom reference pose"""
    pose_id: str = Field(..., description="Unique pose identifier")
    name: str = Field(..., description="Pose name")
    image: str = Field(..., description="Base64 encoded image")
    difficulty: str = Field(default="beginner", description="Difficulty level")
    description: Optional[str] = Field(None, description="Pose instructions")


# Response Schemas
class DetectPoseResponse(BaseModel):
    """Response from pose detection"""
    success: bool
    message: str
    pose: Optional[Pose] = None
    error: Optional[str] = None


class CalculateAccuracyResponse(BaseModel):
    """Response from accuracy calculation"""
    success: bool
    message: str
    accuracy: Optional[AccuracyResult] = None
    error: Optional[str] = None


class ReferencePoseSummary(BaseModel):
    """Summary of reference pose for listing"""
    pose_id: str
    base_pose_name: str
    name: str
    difficulty: str
    view_angle: str
    has_front: bool = False
    has_side: bool = False
    thumbnail: Optional[str] = None


class ListReferencePosesResponse(BaseModel):
    """Response for listing reference poses"""
    success: bool
    message: str
    poses: List[ReferencePoseSummary]
    total_count: int


class GetReferencePoseResponse(BaseModel):
    """Response for getting single reference pose"""
    success: bool
    message: str
    pose: Optional[ReferencePose] = None
    error: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
