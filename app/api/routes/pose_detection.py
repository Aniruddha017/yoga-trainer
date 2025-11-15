from fastapi import APIRouter, HTTPException
from app.models.schemas import DetectPoseRequest, DetectPoseResponse
from app.services.pose_detector import get_pose_detector

router = APIRouter(prefix="/pose-detection", tags=["Pose Detection"])


@router.post("/detect-pose", response_model=DetectPoseResponse)
async def detect_pose(request: DetectPoseRequest):
    """
    Detect pose from base64 encoded image
    
    Args:
        request: DetectPoseRequest with base64 image
        
    Returns:
        DetectPoseResponse with detected keypoints
    """
    try:
        # Get pose detector
        detector = get_pose_detector()
        
        # Detect pose
        pose = detector.detect_pose_from_base64(request.image)
        
        if pose is None:
            return DetectPoseResponse(
                success=False,
                message="No pose detected in the image. Please ensure you are clearly visible in front of the camera.",
                pose=None,
                error="No pose landmarks found"
            )
        
        # Check confidence
        if pose.confidence < 0.5:
            return DetectPoseResponse(
                success=False,
                message=f"Low confidence detection ({pose.confidence:.2%}). Please improve lighting and ensure full body is visible.",
                pose=None,
                error=f"Low confidence: {pose.confidence:.2%}"
            )
        
        return DetectPoseResponse(
            success=True,
            message=f"Pose detected successfully with {pose.confidence:.2%} confidence",
            pose=pose,
            error=None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting pose: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for pose detection service"""
    return {
        "status": "healthy",
        "service": "pose-detection",
        "message": "Pose detection service is running"
    }
