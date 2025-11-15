"""
Script to process yoga pose images and extract keypoints for both front and side views
Place your images inside each pose folder (e.g., Tree_Pose_or_Vrksasana__front/image.jpg)
"""

import sys
import json
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pose_detector import get_pose_detector


def process_reference_poses():
    """Process all yoga pose images in the reference_poses/images directory"""
    
    base_dir = Path(__file__).parent.parent
    images_dir = base_dir / "data" / "reference_poses" / "images"
    keypoints_dir = base_dir / "data" / "reference_poses" / "keypoints"
    
    # Create keypoints directory if it doesn't exist
    keypoints_dir.mkdir(parents=True, exist_ok=True)
    
    # Get pose detector
    print("Initializing MediaPipe Pose detector...")
    detector = get_pose_detector()
    
    # Track processed poses
    processed_count = 0
    failed_count = 0
    
    # Iterate through all pose folders
    for pose_folder in sorted(images_dir.iterdir()):
        if not pose_folder.is_dir():
            continue
        
        folder_name = pose_folder.name
        
        # Determine if this is front or side view
        if folder_name.endswith("_front"):
            view_angle = "front"
            base_pose_name = folder_name[:-6]  # Remove "_front"
        elif folder_name.endswith("_side"):
            view_angle = "side"
            base_pose_name = folder_name[:-5]  # Remove "_side"
        else:
            print(f"⚠️  Skipping folder (no _front or _side suffix): {folder_name}")
            continue
        
        # Find image in folder (support jpg, jpeg, png)
        image_files = list(pose_folder.glob("*.jpg")) + \
                     list(pose_folder.glob("*.jpeg")) + \
                     list(pose_folder.glob("*.png"))
        
        if not image_files:
            print(f"⚠️  No image found in: {folder_name}")
            continue
        
        # Use first image found
        image_file = image_files[0]
        
        print(f"\n📸 Processing: {folder_name}")
        print(f"   Image: {image_file.name}")
        print(f"   View: {view_angle}")
        
        try:
            # Detect pose
            pose = detector.detect_pose_from_file(str(image_file))
            
            if pose is None:
                print(f"   ❌ Failed: No pose detected")
                failed_count += 1
                continue
            
            if pose.confidence < 0.5:
                print(f"   ⚠️  Warning: Low confidence ({pose.confidence:.2%})")
            
            # Create pose ID (combine base name and view)
            pose_id = f"{base_pose_name}_{view_angle}"
            
            # Clean up pose name for display
            display_name = base_pose_name.replace("_", " ").replace("  ", " ")
            
            # Create reference pose data
            pose_data = {
                "pose_id": pose_id,
                "base_pose_name": base_pose_name,
                "name": display_name,
                "difficulty": "intermediate",  # Default, can be updated manually
                "view_angle": view_angle,
                "keypoints": [
                    {
                        "landmark_id": kp.landmark_id,
                        "name": kp.name,
                        "x": kp.x,
                        "y": kp.y,
                        "z": kp.z,
                        "visibility": kp.visibility
                    }
                    for kp in pose.keypoints
                ],
                "reference_image": f"data/reference_poses/images/{folder_name}/{image_file.name}",
                "description": f"{display_name} - {view_angle.capitalize()} view"
            }
            
            # Save keypoints JSON
            keypoints_file = keypoints_dir / f"{pose_id}.json"
            with open(keypoints_file, 'w') as f:
                json.dump(pose_data, f, indent=2)
            
            print(f"   ✅ Success! Confidence: {pose.confidence:.2%}")
            print(f"   💾 Saved: {keypoints_file.name}")
            processed_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            failed_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Processing Complete!")
    print(f"✅ Successfully processed: {processed_count} poses")
    print(f"❌ Failed: {failed_count} poses")
    print(f"{'='*60}")


if __name__ == "__main__":
    print("🧘 Yoga Pose Reference Image Processor")
    print("="*60)
    process_reference_poses()
