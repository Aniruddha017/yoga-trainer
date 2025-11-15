from fastapi import APIRouter, HTTPException
from app.models.schemas import CalculateAccuracyRequest, CalculateAccuracyResponse
from app.services.accuracy_calculator import get_accuracy_calculator
from app.config import settings
import json
from pathlib import Path

router = APIRouter(prefix="/accuracy", tags=["Accuracy"])


@router.post("/calculate-accuracy", response_model=CalculateAccuracyResponse)
async def calculate_accuracy(request: CalculateAccuracyRequest):
    """
    Calculate pose accuracy by comparing user keypoints with reference pose
    
    Args:
        request: CalculateAccuracyRequest with user keypoints and reference pose ID
        
    Returns:
        CalculateAccuracyResponse with accuracy scores and feedback
    """
    try:
        # Load reference pose
        reference_file = settings.reference_keypoints_dir / f"{request.reference_pose_id}.json"
        
        if not reference_file.exists():
            return CalculateAccuracyResponse(
                success=False,
                message=f"Reference pose '{request.reference_pose_id}' not found",
                accuracy=None,
                error=f"Reference pose file not found: {reference_file}"
            )
        
        # Read reference pose
        with open(reference_file, 'r') as f:
            reference_data = json.load(f)
        
        # Extract reference keypoints
        from app.models.pose import Keypoint
        reference_keypoints = [
            Keypoint(**kp) for kp in reference_data.get("keypoints", [])
        ]
        
        if not reference_keypoints:
            return CalculateAccuracyResponse(
                success=False,
                message="Invalid reference pose data",
                accuracy=None,
                error="No keypoints found in reference pose"
            )
        
        # Get accuracy calculator
        calculator = get_accuracy_calculator()
        
        # Calculate accuracy
        accuracy_result = calculator.calculate_accuracy(
            reference_keypoints=reference_keypoints,
            user_keypoints=request.user_keypoints
        )
        
        return CalculateAccuracyResponse(
            success=True,
            message=f"Accuracy calculated: {accuracy_result.overall_accuracy:.2f}%",
            accuracy=accuracy_result,
            error=None
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Error calculating accuracy: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating accuracy: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for accuracy service"""
    return {
        "status": "healthy",
        "service": "accuracy",
        "message": "Accuracy calculation service is running"
    }
