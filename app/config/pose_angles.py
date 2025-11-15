"""
Manual angle definitions for each yoga pose.
Each pose specifies which joint angles to measure and their target values.
"""

from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field


class AngleDefinition(BaseModel):
    """Definition of a joint angle to measure"""
    name: str = Field(..., description="Name of the angle (e.g., 'left_elbow')")
    points: Tuple[str, str, str] = Field(..., description="(point1, vertex, point2) landmark names")
    target_angle: float = Field(..., description="Expected angle in degrees")
    tolerance: float = Field(default=15.0, description="Acceptable deviation in degrees")
    weight: float = Field(default=1.0, description="Importance weight (higher = more important)")


class ConnectionDefinition(BaseModel):
    """Definition of a body part connection to check (e.g., hand holds foot)"""
    name: str = Field(..., description="Name of the connection (e.g., 'Left hand holds right foot')")
    point1: str = Field(..., description="First keypoint (e.g., 'left_wrist')")
    point2: str = Field(..., description="Second keypoint (e.g., 'right_ankle')")
    max_distance: float = Field(default=0.1, description="Maximum normalized distance to be considered 'connected'")
    weight: float = Field(default=1.0, description="Importance weight")


class PoseAngleConfig(BaseModel):
    """Angle configuration for a specific pose"""
    pose_name: str = Field(..., description="Base name of the pose")
    view: str = Field(..., description="Camera view: 'front' or 'side'")
    required_angles: List[AngleDefinition] = Field(..., description="List of angles to measure")
    required_keypoints: List[str] = Field(..., description="Only these keypoints will be checked")
    required_connections: Optional[List[ConnectionDefinition]] = Field(default=None, description="Body part connections to check (e.g., hand holds foot)")


# Define angles for each pose
POSE_ANGLE_DEFINITIONS: Dict[str, PoseAngleConfig] = {
    
    # Tree Pose (Front View)
    "Akarna_Dhanurasana_front": PoseAngleConfig(
        pose_name="Akarna_Dhanurasana_",
        view="front",
        required_keypoints=[
            "nose", "left_shoulder", "right_shoulder",
            "left_elbow", "right_elbow",
            "left_wrist", "right_wrist",
            "left_hip", "right_hip",
            "left_knee", "right_knee",
            "left_ankle", "right_ankle"
        ],
        required_connections=[
            ConnectionDefinition(
                name="Left hand holds right foot",
                point1="left_wrist",
                point2="right_ankle",
                max_distance=0.35,  # 15% of normalized space
                weight=2.0
            ),
            ConnectionDefinition(
                name="Right hand holds left foot",
                point1="right_wrist",
                point2="left_ankle",
                max_distance=0.35,
                weight=2.0
            )
        ],
        required_angles=[
            AngleDefinition(
                name="Standing Leg (Right Knee)",
                points=("right_hip", "right_knee", "right_ankle"),
                target_angle=56.2,  # Straight standing leg
                tolerance=25.0,
                weight=5.0  # Most critical
            ),
            AngleDefinition(
                name="right hand",
                points=("right_shoulder", "right_elbow", "right_wrist"),
                target_angle=173.9,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hand",
                points=("left_shoulder", "left_elbow", "left_wrist"),  # TODO: Update with actual keypoint names
                target_angle=39.3,
                tolerance=25.0,
                weight=2.0
            ),
            # AngleDefinition(
            #     name="Hips Level",
            #     points=("left_hip", "right_hip", "right_knee"),
            #     target_angle=180.0,  # Hips should be level
            #     tolerance=10.0,
            #     weight=1.5
            # ),
            # AngleDefinition(
            #     name="Arms (Left Elbow)",
            #     points=("left_shoulder", "left_elbow", "left_wrist"),
            #     target_angle=90.0,  # Prayer hands position
            #     tolerance=30.0,
            #     weight=1.0
            # ),
            # AngleDefinition(
            #     name="Arms (Right Elbow)",
            #     points=("right_shoulder", "right_elbow", "right_wrist"),
            #     target_angle=90.0,
            #     tolerance=30.0,
            #     weight=1.0
            # ),
        ]
    ),
    
    # Tree Pose (Side View)
    "Tree_Pose_or_Vrksasana__side": PoseAngleConfig(
        pose_name="Tree_Pose_or_Vrksasana_",
        view="side",
        required_keypoints=[
            "nose", "left_shoulder", "left_elbow", "left_wrist",
            "left_hip", "left_knee", "left_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Body Alignment",
                points=("left_shoulder", "left_hip", "left_ankle"),
                target_angle=180.0,  # Straight vertical line
                tolerance=10.0,
                weight=3.0
            ),
            AngleDefinition(
                name="Hip Angle",
                points=("left_shoulder", "left_hip", "left_knee"),
                target_angle=160.0,  # Slight backward lean
                tolerance=15.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Standing Leg",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=180.0,  # Straight leg
                tolerance=5.0,
                weight=2.5
            ),
        ]
    ),
    
    # Warrior I Pose (Front View)
    "Warrior_I_Pose_or_Virabhadrasana_I__front": PoseAngleConfig(
        pose_name="Warrior_I_Pose_or_Virabhadrasana_I_",
        view="front",
        required_keypoints=[
            "left_shoulder", "right_shoulder",
            "left_elbow", "right_elbow",
            "left_wrist", "right_wrist",
            "left_hip", "right_hip",
            "left_knee", "right_knee",
            "left_ankle", "right_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Front Knee (Left)",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=90.0,  # Bent at 90 degrees
                tolerance=15.0,
                weight=3.0  # Most important
            ),
            AngleDefinition(
                name="Back Leg (Right)",
                points=("right_hip", "right_knee", "right_ankle"),
                target_angle=180.0,  # Straight
                tolerance=10.0,
                weight=2.5
            ),
            AngleDefinition(
                name="Left Arm Raised",
                points=("left_shoulder", "left_elbow", "left_wrist"),
                target_angle=180.0,  # Straight arm up
                tolerance=10.0,
                weight=1.5
            ),
            AngleDefinition(
                name="Right Arm Raised",
                points=("right_shoulder", "right_elbow", "right_wrist"),
                target_angle=180.0,
                tolerance=10.0,
                weight=1.5
            ),
            AngleDefinition(
                name="Shoulders Level",
                points=("left_shoulder", "left_hip", "right_shoulder"),
                target_angle=180.0,
                tolerance=10.0,
                weight=1.5
            ),
            AngleDefinition(
                name="Arms Overhead (Left)",
                points=("left_elbow", "left_shoulder", "left_hip"),
                target_angle=180.0,  # Arms straight overhead
                tolerance=15.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Arms Overhead (Right)",
                points=("right_elbow", "right_shoulder", "right_hip"),
                target_angle=180.0,
                tolerance=15.0,
                weight=2.0
            ),
        ]
    ),
    
    # Warrior I Pose (Side View)
    "Warrior_I_Pose_or_Virabhadrasana_I__side": PoseAngleConfig(
        pose_name="Warrior_I_Pose_or_Virabhadrasana_I_",
        view="side",
        required_keypoints=[
            "nose", "left_shoulder", "left_elbow", "left_wrist",
            "left_hip", "left_knee", "left_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Front Knee",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=90.0,
                tolerance=15.0,
                weight=3.0  # Critical
            ),
            AngleDefinition(
                name="Torso Upright",
                points=("left_shoulder", "left_hip", "left_knee"),
                target_angle=160.0,  # Slight forward lean
                tolerance=15.0,
                weight=2.5
            ),
            AngleDefinition(
                name="Arm Overhead",
                points=("left_elbow", "left_shoulder", "left_hip"),
                target_angle=180.0,  # Arms vertical
                tolerance=15.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Arm Straight",
                points=("left_shoulder", "left_elbow", "left_wrist"),
                target_angle=180.0,
                tolerance=10.0,
                weight=1.5
            ),
        ]
    ),
    
    # Downward-Facing Dog (Side View)
    "Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana__side": PoseAngleConfig(
        pose_name="Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana_",
        view="side",
        required_keypoints=[
            "left_wrist", "left_elbow", "left_shoulder",
            "left_hip", "left_knee", "left_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Inverted V (Shoulder Angle)",
                points=("left_wrist", "left_shoulder", "left_hip"),
                target_angle=90.0,  # Forms inverted V
                tolerance=15.0,
                weight=3.0
            ),
            AngleDefinition(
                name="Hip Angle",
                points=("left_shoulder", "left_hip", "left_knee"),
                target_angle=90.0,
                tolerance=15.0,
                weight=3.0
            ),
            AngleDefinition(
                name="Arm Straight",
                points=("left_wrist", "left_elbow", "left_shoulder"),
                target_angle=180.0,
                tolerance=10.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Leg Straight",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=180.0,
                tolerance=10.0,
                weight=2.0
            ),
        ]
    ),
    
    # Plank Pose (Side View)
    "Plank_Pose_or_Kumbhakasana__side": PoseAngleConfig(
        pose_name="Plank_Pose_or_Kumbhakasana_",
        view="side",
        required_keypoints=[
            "nose", "left_shoulder", "left_elbow", "left_wrist",
            "left_hip", "left_knee", "left_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Body Straight Line",
                points=("left_shoulder", "left_hip", "left_ankle"),
                target_angle=180.0,  # Perfect straight line
                tolerance=5.0,
                weight=3.5  # Most critical
            ),
            AngleDefinition(
                name="Arm Position",
                points=("left_wrist", "left_elbow", "left_shoulder"),
                target_angle=180.0,  # Straight arms
                tolerance=10.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Shoulder Over Wrists",
                points=("left_wrist", "left_shoulder", "left_hip"),
                target_angle=90.0,
                tolerance=10.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Leg Straight",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=180.0,
                tolerance=5.0,
                weight=1.5
            ),
        ]
    ),
    
    # Mountain Pose (Front View)
    "Mountain_Pose_or_Tadasana__front": PoseAngleConfig(
        pose_name="Mountain_Pose_or_Tadasana_",
        view="front",
        required_keypoints=[
            "nose", "left_shoulder", "right_shoulder",
            "left_hip", "right_hip",
            "left_knee", "right_knee",
            "left_ankle", "right_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Left Leg Straight",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=180.0,
                tolerance=5.0,
                weight=2.5
            ),
            AngleDefinition(
                name="Right Leg Straight",
                points=("right_hip", "right_knee", "right_ankle"),
                target_angle=180.0,
                tolerance=5.0,
                weight=2.5
            ),
            AngleDefinition(
                name="Shoulders Level",
                points=("left_shoulder", "left_hip", "right_shoulder"),
                target_angle=180.0,
                tolerance=5.0,
                weight=2.0
            ),
            AngleDefinition(
                name="Hips Level",
                points=("left_hip", "right_hip", "right_knee"),
                target_angle=180.0,
                tolerance=5.0,
                weight=2.0
            ),
        ]
    ),
    
    # Child's Pose (Side View)
    "Child_Pose_or_Balasana__side": PoseAngleConfig(
        pose_name="Child_Pose_or_Balasana_",
        view="side",
        required_keypoints=[
            "nose", "left_shoulder", "left_elbow", "left_wrist",
            "left_hip", "left_knee", "left_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="Hip Flexion",
                points=("left_shoulder", "left_hip", "left_knee"),
                target_angle=45.0,  # Deep fold
                tolerance=15.0,
                weight=3.0
            ),
            AngleDefinition(
                name="Knee Bend",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=45.0,  # Sitting on heels
                tolerance=20.0,
                weight=2.5
            ),
            AngleDefinition(
                name="Arms Extended",
                points=("left_wrist", "left_shoulder", "left_hip"),
                target_angle=30.0,  # Arms reaching forward
                tolerance=20.0,
                weight=1.5
            ),
        ]
    ),
    
}


def get_pose_config(pose_id: str) -> PoseAngleConfig:
    """
    Get angle configuration for a specific pose ID
    
    Args:
        pose_id: Pose identifier (e.g., 'Tree_Pose_or_Vrksasana__front')
        
    Returns:
        PoseAngleConfig for the pose
        
    Raises:
        ValueError: If pose configuration not found
    """
    if pose_id not in POSE_ANGLE_DEFINITIONS:
        raise ValueError(f"No angle configuration found for pose: {pose_id}")
    return POSE_ANGLE_DEFINITIONS[pose_id]


def list_configured_poses() -> List[str]:
    """List all poses that have angle configurations"""
    return sorted(list(POSE_ANGLE_DEFINITIONS.keys()))


def has_config(pose_id: str) -> bool:
    """Check if a pose has manual angle configuration"""
    return pose_id in POSE_ANGLE_DEFINITIONS
