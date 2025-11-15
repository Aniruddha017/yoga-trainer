from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ListReferencePosesResponse,
    GetReferencePoseResponse,
    ReferencePoseSummary,
    UploadReferencePoseRequest
)
from app.models.pose import ReferencePose, Keypoint
from app.services.pose_detector import get_pose_detector
from app.config import settings
import json
from pathlib import Path
import base64

router = APIRouter(prefix="/reference", tags=["Reference Poses"])


@router.get("/poses", response_model=ListReferencePosesResponse)
async def list_reference_poses():
    """
    List all available reference poses grouped by base pose name
    Shows which views (front/side) are available for each pose
    
    Returns:
        ListReferencePosesResponse with list of available poses
    """
    try:
        poses_dict = {}  # Group by base_pose_name
        keypoints_dir = settings.reference_keypoints_dir
        
        # Check if directory exists
        if not keypoints_dir.exists():
            keypoints_dir.mkdir(parents=True, exist_ok=True)
            return ListReferencePosesResponse(
                success=True,
                message="No reference poses found. Please add reference poses to get started.",
                poses=[],
                total_count=0
            )
        
        # Iterate through all JSON files
        for pose_file in keypoints_dir.glob("*.json"):
            try:
                with open(pose_file, 'r') as f:
                    pose_data = json.load(f)
                
                pose_id = pose_data.get("pose_id", pose_file.stem)
                base_pose_name = pose_data.get("base_pose_name", pose_id.rsplit("_", 1)[0])
                view_angle = pose_data.get("view_angle", "front")
                
                # Initialize or update base pose entry
                if base_pose_name not in poses_dict:
                    poses_dict[base_pose_name] = {
                        "base_pose_name": base_pose_name,
                        "name": pose_data.get("name", base_pose_name.replace("_", " ").title()),
                        "difficulty": pose_data.get("difficulty", "beginner"),
                        "has_front": False,
                        "has_side": False,
                        "pose_id_front": None,
                        "pose_id_side": None,
                        "thumbnail": None
                    }
                
                # Update view availability
                if view_angle == "front":
                    poses_dict[base_pose_name]["has_front"] = True
                    poses_dict[base_pose_name]["pose_id_front"] = pose_id
                    
                    # Try to get thumbnail for front view
                    if not poses_dict[base_pose_name]["thumbnail"] and "reference_image" in pose_data:
                        image_path = settings.base_dir / pose_data["reference_image"]
                        if image_path.exists():
                            try:
                                with open(image_path, 'rb') as img_file:
                                    image_bytes = img_file.read()
                                    poses_dict[base_pose_name]["thumbnail"] = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
                            except:
                                pass
                                
                elif view_angle == "side":
                    poses_dict[base_pose_name]["has_side"] = True
                    poses_dict[base_pose_name]["pose_id_side"] = pose_id
            
            except Exception as e:
                print(f"Error loading pose {pose_file}: {e}")
                continue
        
        # Convert to list of ReferencePoseSummary
        poses = []
        for base_name, data in sorted(poses_dict.items()):
            # Use front view as default, fallback to side
            default_pose_id = data["pose_id_front"] if data["has_front"] else data["pose_id_side"]
            default_view = "front" if data["has_front"] else "side"
            
            poses.append(ReferencePoseSummary(
                pose_id=default_pose_id,
                base_pose_name=data["base_pose_name"],
                name=data["name"],
                difficulty=data["difficulty"],
                view_angle=default_view,
                has_front=data["has_front"],
                has_side=data["has_side"],
                thumbnail=data["thumbnail"]
            ))
        
        return ListReferencePosesResponse(
            success=True,
            message=f"Found {len(poses)} reference poses",
            poses=poses,
            total_count=len(poses)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing reference poses: {str(e)}"
        )


@router.get("/poses/{pose_id}", response_model=GetReferencePoseResponse)
async def get_reference_pose(pose_id: str):
    """
    Get detailed information about a specific reference pose
    
    Args:
        pose_id: ID of the pose to retrieve (e.g., "Tree_Pose_front" or "Tree_Pose_side")
        
    Returns:
        GetReferencePoseResponse with complete pose data
    """
    try:
        pose_file = settings.reference_keypoints_dir / f"{pose_id}.json"
        
        if not pose_file.exists():
            return GetReferencePoseResponse(
                success=False,
                message=f"Reference pose '{pose_id}' not found",
                pose=None,
                error="Pose file not found"
            )
        
        with open(pose_file, 'r') as f:
            pose_data = json.load(f)
        
        # Load thumbnail if image exists
        thumbnail = None
        if "reference_image" in pose_data:
            image_path = settings.base_dir / pose_data["reference_image"]
            if image_path.exists():
                with open(image_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                    thumbnail = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
        
        # Create ReferencePose object
        keypoints = [Keypoint(**kp) for kp in pose_data.get("keypoints", [])]
        
        reference_pose = ReferencePose(
            pose_id=pose_data.get("pose_id", pose_id),
            base_pose_name=pose_data.get("base_pose_name"),
            name=pose_data.get("name", "Unknown Pose"),
            difficulty=pose_data.get("difficulty", "beginner"),
            view_angle=pose_data.get("view_angle", "front"),
            keypoints=keypoints,
            reference_image=pose_data.get("reference_image"),
            thumbnail=thumbnail,
            description=pose_data.get("description")
        )
        
        return GetReferencePoseResponse(
            success=True,
            message=f"Retrieved pose: {reference_pose.name}",
            pose=reference_pose,
            error=None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving reference pose: {str(e)}"
        )


@router.get("/poses/by-base/{base_pose_name}/views", response_model=dict)
async def get_pose_views(base_pose_name: str):
    """
    Get available views (front/side) for a specific base pose
    
    Args:
        base_pose_name: Base name of the pose (e.g., "Tree_Pose")
        
    Returns:
        Dictionary with available views and their pose IDs
    """
    try:
        views = {
            "base_pose_name": base_pose_name,
            "available_views": [],
            "front": None,
            "side": None
        }
        
        keypoints_dir = settings.reference_keypoints_dir
        
        # Look for front and side versions
        for pose_file in keypoints_dir.glob(f"{base_pose_name}_*.json"):
            try:
                with open(pose_file, 'r') as f:
                    pose_data = json.load(f)
                
                view_angle = pose_data.get("view_angle", "front")
                pose_id = pose_data.get("pose_id", pose_file.stem)
                
                if view_angle == "front":
                    views["front"] = pose_id
                    views["available_views"].append("front")
                elif view_angle == "side":
                    views["side"] = pose_id
                    views["available_views"].append("side")
            except:
                continue
        
        if not views["available_views"]:
            raise HTTPException(
                status_code=404,
                detail=f"No views found for pose: {base_pose_name}"
            )
        
        return {
            "success": True,
            "message": f"Found {len(views['available_views'])} views",
            "data": views
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pose views: {str(e)}"
        )


@router.post("/poses/upload")
async def upload_reference_pose(request: UploadReferencePoseRequest):
    """
    Upload a new reference pose (processes image with MediaPipe)
    
    Args:
        request: UploadReferencePoseRequest with image and metadata
        
    Returns:
        Success message with pose ID
    """
    try:
        # Get pose detector
        detector = get_pose_detector()
        
        # Detect pose from uploaded image
        pose = detector.detect_pose_from_base64(request.image)
        
        if pose is None or pose.confidence < 0.7:
            raise HTTPException(
                status_code=400,
                detail="Could not detect pose in uploaded image or confidence too low"
            )
        
        # Save image
        image_filename = f"{request.pose_id}.jpg"
        image_path = settings.reference_images_dir / image_filename
        
        # Decode and save image
        image_data = request.image.split(",")[1] if "," in request.image else request.image
        image_bytes = base64.b64decode(image_data)
        
        settings.reference_images_dir.mkdir(parents=True, exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Create reference pose data
        reference_data = {
            "pose_id": request.pose_id,
            "name": request.name,
            "difficulty": request.difficulty,
            "view_angle": "front",
            "keypoints": [kp.dict() for kp in pose.keypoints],
            "reference_image": f"data/reference_poses/images/{image_filename}",
            "description": request.description
        }
        
        # Save keypoints JSON
        keypoints_file = settings.reference_keypoints_dir / f"{request.pose_id}.json"
        settings.reference_keypoints_dir.mkdir(parents=True, exist_ok=True)
        
        with open(keypoints_file, 'w') as f:
            json.dump(reference_data, f, indent=2)
        
        return {
            "success": True,
            "message": f"Reference pose '{request.name}' uploaded successfully",
            "pose_id": request.pose_id,
            "confidence": pose.confidence
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading reference pose: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for reference pose service"""
    return {
        "status": "healthy",
        "service": "reference-poses",
        "message": "Reference pose service is running"
    }
