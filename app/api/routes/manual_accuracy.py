"""
API routes for manual angle-based accuracy calculation
"""

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import json
from pathlib import Path
from app.models.pose import Keypoint
from app.services.manual_accuracy_calculator import get_manual_accuracy_calculator
from app.config.pose_angles import list_configured_poses, get_pose_config, has_config
from app.config import settings


router = APIRouter(prefix="/manual-accuracy", tags=["Manual Accuracy"])

calculator = get_manual_accuracy_calculator()


class ManualAccuracyRequest(BaseModel):
    """Request for manual accuracy calculation"""
    user_keypoints: List[Keypoint]
    pose_id: str
    use_position_matching: bool = True  # Enable position matching by default


@router.post("/calculate")
async def calculate_manual_accuracy(request: ManualAccuracyRequest):
    """
    Calculate accuracy using manually defined angles and optional position matching
    
    This endpoint uses:
    1. Predefined target angles for each pose (primary)
    2. Position matching against reference keypoints (optional, enabled by default)
    """
    try:
        # Load reference keypoints if position matching is enabled
        reference_keypoints = None
        if request.use_position_matching:
            keypoint_file = settings.reference_keypoints_dir / f"{request.pose_id}.json"
            print(f"DEBUG: Looking for reference keypoints at: {keypoint_file}")
            print(f"DEBUG: File exists: {keypoint_file.exists()}")
            
            if keypoint_file.exists():
                try:
                    with open(keypoint_file, 'r') as f:
                        keypoint_data = json.load(f)
                        reference_keypoints = [Keypoint(**kp) for kp in keypoint_data.get("keypoints", [])]
                        print(f"DEBUG: Loaded {len(reference_keypoints)} reference keypoints")
                except Exception as e:
                    print(f"Warning: Could not load reference keypoints for {request.pose_id}: {e}")
            else:
                print(f"DEBUG: Reference keypoint file not found for {request.pose_id}")
        
        result = calculator.calculate_accuracy(
            user_keypoints=request.user_keypoints,
            pose_id=request.pose_id,
            reference_keypoints=reference_keypoints
        )
        
        if result.get("error"):
            return {
                "success": False,
                "message": result["error"],
                "data": result
            }
        
        return {
            "success": True,
            "message": f"Accuracy calculated: {result['overall_accuracy']:.1f}%",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = f"Error calculating manual accuracy: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configured-poses")
async def get_configured_poses():
    """
    Get list of poses that have manual angle configurations
    
    Returns:
        List of pose IDs with manual angle definitions
    """
    return {
        "success": True,
        "poses": list_configured_poses(),
        "count": len(list_configured_poses())
    }


@router.get("/pose-config/{pose_id}")
async def get_pose_angle_config(pose_id: str):
    """
    Get the angle configuration for a specific pose
    
    Args:
        pose_id: Pose identifier (e.g., 'Tree_Pose_or_Vrksasana__front')
        
    Returns:
        Angle definitions and required keypoints for the pose
    """
    try:
        if not has_config(pose_id):
            raise HTTPException(
                status_code=404,
                detail=f"No manual angle configuration found for: {pose_id}"
            )
        
        config = get_pose_config(pose_id)
        
        return {
            "success": True,
            "pose_id": pose_id,
            "pose_name": config.pose_name,
            "view": config.view,
            "required_keypoints": config.required_keypoints,
            "angles": [
                {
                    "name": angle.name,
                    "points": list(angle.points),
                    "target_angle": angle.target_angle,
                    "tolerance": angle.tolerance,
                    "weight": angle.weight
                }
                for angle in config.required_angles
            ],
            "total_angles": len(config.required_angles)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/check/{pose_id}")
async def check_if_configured(pose_id: str):
    """
    Check if a pose has manual angle configuration
    
    Args:
        pose_id: Pose identifier
        
    Returns:
        Boolean indicating if configuration exists
    """
    return {
        "pose_id": pose_id,
        "has_manual_config": has_config(pose_id),
        "message": "Manual angles defined" if has_config(pose_id) else "Using default accuracy calculation"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for manual accuracy service"""
    return {
        "status": "healthy",
        "service": "manual_accuracy",
        "message": "Manual angle-based accuracy service is running",
        "configured_poses_count": len(list_configured_poses())
    }
