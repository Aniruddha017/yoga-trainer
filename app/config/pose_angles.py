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
          
        ]
    ),

     "Boat_Pose_or_Paripurna_Navasana__front": PoseAngleConfig(
        pose_name="Boat_Pose_or_Paripurna_Navasana__",
        view="side",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="left hand",
                points=("left_shoulder", "left_elbow", "left_wrist"),
                target_angle=175.8,
                tolerance=25.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left leg",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=179.7,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="right leg",
                points=("right_hip", "right_knee", "right_ankle"),
                target_angle=179.8,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="right hand",
                points=("right_shoulder", "right_elbow", "right_wrist"),
                target_angle=169.2,
                tolerance=25.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hip",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=83.5,
                tolerance=25.0,
                weight=5.0
            ),
        ]
    ),





    # Bound_Angle_Pose_or_Baddha_Konasana__image_179 (Front View)
    "Bound_Angle_Pose_or_Baddha_Konasana__front": PoseAngleConfig(
        pose_name="Bound_Angle_Pose_or_Baddha_Konasana__",
        view="front",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
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
                name="right hand",
                points=("right_shoulder", "right_elbow", "right_wrist"),
                target_angle=175.4,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hand",
                points=("left_shoulder", "left_elbow", "left_wrist"),
                target_angle=178.4,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="right leg",
                points=("right_hip", "right_knee", "right_ankle"),
                target_angle=16.9,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="left leg",
                points=("left_hip", "left_knee", "left_ankle"),
                target_angle=13.2,
                tolerance=25.0,
                weight=4.0
            ),
        ]
    ),

    # Bow_Pose_or_Dhanurasana__ (Side View)
    "Bow_Pose_or_Dhanurasana__side": PoseAngleConfig(
        pose_name="Bow_Pose_or_Dhanurasana__",
        view="side",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
        ],
          required_connections=[
            ConnectionDefinition(
                name="Left hand holds left foot",
                point1="left_wrist",
                point2="left_ankle",
                max_distance=0.35,  # 15% of normalized space
                weight=2.0
            ),
            ConnectionDefinition(
                name="Right hand holds right foot",
                point1="right_wrist",
                point2="right_ankle",
                max_distance=0.35,
                weight=2.0
            )
        ],
        required_angles=[
            AngleDefinition(
                name="right hand",
                points=('right_shoulder', 'right_elbow', 'right_wrist'),
                target_angle=169.9,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hand",
                points=('left_shoulder', 'left_elbow', 'left_wrist'),
                target_angle=168.1,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="right leg",
                points=('right_hip', 'right_knee', 'right_ankle'),
                target_angle=85.7,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="left leg",
                points=('left_hip', 'left_knee', 'left_ankle'),
                target_angle=95.4,
                tolerance=25.0,
                weight=4.0
            ),
        ]
    ),

    # Bridge_Pose_or_Setu_Bandha_Sarvangasana__ (Side View)
    "Bridge_Pose_or_Setu_Bandha_Sarvangasana__front": PoseAngleConfig(
        pose_name="Bridge_Pose_or_Setu_Bandha_Sarvangasana__",
        view="front",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
        ],
        required_connections=[
            ConnectionDefinition(
                name="Left hand holds left foot",
                point1="left_wrist",
                point2="left_ankle",
                max_distance=0.35,  # 15% of normalized space
                weight=2.0
            ),
            ConnectionDefinition(
                name="Right hand holds right foot",
                point1="right_wrist",
                point2="right_ankle",
                max_distance=0.35,
                weight=2.0
            )
        ],
        required_angles=[
            AngleDefinition(
                name="right leg",
                points=('right_hip', 'right_knee', 'right_ankle'),
                target_angle=63.5,
                tolerance=20.0,
                weight=4.0
            ),
            AngleDefinition(
                name="left leg",
                points=('left_hip', 'left_knee', 'left_ankle'),
                target_angle=61.1,
                tolerance=20.0,
                weight=4.0
            ),
            AngleDefinition(
                name="right hand",
                points=('right_shoulder', 'right_elbow', 'right_wrist'),
                target_angle=177.8,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hand",
                points=('left_shoulder', 'left_elbow', 'left_wrist'),
                target_angle=176.0,
                tolerance=20.0,
                weight=2.0
            ),
        ]
    ),

    # Camel_Pose_or_Ustrasana__ (Side View)
    "Camel_Pose_or_Ustrasana__side": PoseAngleConfig(
        pose_name="Camel_Pose_or_Ustrasana__",
        view="side",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
        ],
                required_connections=[
            ConnectionDefinition(
                name="Left hand holds left foot",
                point1="left_wrist",
                point2="left_ankle",
                max_distance=0.35,  # 15% of normalized space
                weight=2.0
            ),
            ConnectionDefinition(
                name="Right hand holds right foot",
                point1="right_wrist",
                point2="right_ankle",
                max_distance=0.35,
                weight=2.0
            )
        ],
        required_angles=[
            AngleDefinition(
                name="right hand",
                points=('right_shoulder', 'right_elbow', 'right_wrist'),
                target_angle=171.7,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hand",
                points=('left_shoulder', 'left_elbow', 'left_wrist'),
                target_angle=169.4,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="right leg",
                points=('right_hip', 'right_knee', 'right_ankle'),
                target_angle=93.2,
                tolerance=20.0,
                weight=4.0
            ),
            AngleDefinition(
                name="left leg",
                points=('left_hip', 'left_knee', 'left_ankle'),
                target_angle=88.0,
                tolerance=25.0,
                weight=4.0
            ),
        ]
    ),

    # Cat_Cow_Pose_or_Marjaryasana__ (Side View)
    "Cat_Cow_Pose_or_Marjaryasana__side": PoseAngleConfig(
        pose_name="Cat_Cow_Pose_or_Marjaryasana__",
        view="side",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="right hand",
                points=('right_shoulder', 'right_elbow', 'right_wrist'),
                target_angle=179.8,
                tolerance=25.0,
                weight=2.0
            ),
            AngleDefinition(
                name="left hand",
                points=('left_shoulder', 'left_elbow', 'left_wrist'),
                target_angle=179.0,
                tolerance=20.0,
                weight=2.0
            ),
            AngleDefinition(
                name="right leg",
                points=('right_hip', 'right_knee', 'right_ankle'),
                target_angle=105.4,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="left leg",
                points=('left_hip', 'left_knee', 'left_ankle'),
                target_angle=103.1,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="shoulder",
                points=("point1_name", "vertex_name", "point2_name"),  # TODO: Update with actual keypoint names
                target_angle=98.9,
                tolerance=30.0,
                weight=3.0
            ),
        ]
    ),

    # Chair_Pose_or_Utkatasana__ (Side View)
    "Chair_Pose_or_Utkatasana__side": PoseAngleConfig(
        pose_name="Chair_Pose_or_Utkatasana__",
        view="side",
        required_keypoints=[
            "nose",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle"
        ],
        required_angles=[
            AngleDefinition(
                name="right leg",
                points=('right_hip', 'right_knee', 'right_ankle'),
                target_angle=90.5,
                tolerance=25.0,
                weight=2.0
            ),
            AngleDefinition(   
                name="left leg",
                points=('left_hip', 'left_knee', 'left_ankle'),
                target_angle=92.8,
                tolerance=25.0,
                weight=4.0
            ),
            AngleDefinition(
                name="right hand",
                points=('right_shoulder', 'right_elbow', 'right_wrist'),
                target_angle=177.0,
                tolerance=25.0,
                weight=2.0
            ),
            AngleDefinition(
                name="right hand",
                points=("left_shoulder", "left_elbow", "left_wrist"),  # TODO: Update with actual keypoint names
                target_angle=179.4,
                tolerance=25.0,
                weight=2.0
            ),
            AngleDefinition(
                name="shoulder",
                points=("point1_name", "vertex_name", "point2_name"),  # TODO: Update with actual keypoint names
                target_angle=70.7,
                tolerance=30.0,
                weight=4.0
            ),
        ]
    ),

}


def get_pose_config(pose_id: str) -> PoseAngleConfig:
   
    
    return POSE_ANGLE_DEFINITIONS[pose_id]


def list_configured_poses() -> List[str]:
    """List all poses that have angle configurations"""
    return sorted(list(POSE_ANGLE_DEFINITIONS.keys()))


def has_config(pose_id: str) -> bool:
    """Check if a pose has manual angle configuration"""
    return pose_id in POSE_ANGLE_DEFINITIONS
