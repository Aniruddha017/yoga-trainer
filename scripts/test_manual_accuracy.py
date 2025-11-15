"""
Test script for manual angle-based accuracy calculation
Tests if the pose angle configuration works correctly
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.pose_angles import get_pose_config, has_config, list_configured_poses
from app.services.manual_accuracy_calculator import get_manual_accuracy_calculator
from app.services.pose_detector import get_pose_detector
from app.models.pose import Keypoint


def test_pose_config():
    """Test if pose configuration is loaded correctly"""
    print("\n" + "="*70)
    print("TEST 1: Pose Configuration Loading")
    print("="*70)
    
    # Test if Akarna_Dhanurasana_front exists
    pose_id = "Akarna_Dhanurasana_front"
    
    if has_config(pose_id):
        print(f"✓ Configuration found for: {pose_id}")
        
        config = get_pose_config(pose_id)
        print(f"\nPose Details:")
        print(f"  - Pose Name: {config.pose_name}")
        print(f"  - View: {config.view}")
        print(f"  - Required Keypoints: {len(config.required_keypoints)}")
        print(f"  - Required Angles: {len(config.required_angles)}")
        
        print(f"\nAngle Definitions:")
        for i, angle in enumerate(config.required_angles, 1):
            print(f"  {i}. {angle.name}")
            print(f"     Points: {angle.points}")
            print(f"     Target: {angle.target_angle}°, Tolerance: ±{angle.tolerance}°, Weight: {angle.weight}")
        
        return True
    else:
        print(f"✗ Configuration NOT found for: {pose_id}")
        print(f"\nAvailable poses: {list_configured_poses()}")
        return False


def test_with_image(image_path):
    """Test with actual image from reference poses"""
    print("\n" + "="*70)
    print("TEST 2: Image-based Pose Detection and Accuracy")
    print("="*70)
    
    if not Path(image_path).exists():
        print(f"✗ Image not found: {image_path}")
        return False
    
    print(f"✓ Image found: {image_path}")
    
    # Detect pose from image
    detector = get_pose_detector()
    pose = detector.detect_pose_from_file(str(image_path))
    
    if not pose:
        print("✗ No pose detected in image")
        return False
    
    print(f"✓ Pose detected with {len(pose.keypoints)} keypoints")
    print(f"  Confidence: {pose.confidence:.2%}")
    
    # Test manual accuracy calculation
    pose_id = "Akarna_Dhanurasana_front"
    calculator = get_manual_accuracy_calculator()
    
    print(f"\nCalculating accuracy for: {pose_id}")
    result = calculator.calculate_accuracy(
        user_keypoints=pose.keypoints,
        pose_id=pose_id
    )
    
    if result.get("error"):
        print(f"✗ Error: {result['error']}")
        return False
    
    print(f"\n✓ Accuracy Calculation Successful!")
    print(f"\n{'='*70}")
    print(f"RESULTS:")
    print(f"{'='*70}")
    print(f"Overall Accuracy: {result['overall_accuracy']:.1f}%")
    print(f"Using Manual Angles: {result.get('using_manual_angles', False)}")
    print(f"\nGeneral Feedback: {result['general_feedback']}")
    
    print(f"\n{'='*70}")
    print(f"Angle-by-Angle Breakdown:")
    print(f"{'='*70}")
    
    for angle_score in result['angle_scores']:
        status_symbol = angle_score['symbol']
        status_color = angle_score['status']
        
        print(f"\n{status_symbol} {angle_score['angle_name']} [{status_color.upper()}]")
        print(f"   Target: {angle_score['target_angle']}°")
        print(f"   Actual: {angle_score['actual_angle']}°")
        print(f"   Deviation: {angle_score['deviation']}°")
        print(f"   Score: {angle_score['score']:.1f}% (weight: {angle_score['weight']})")
    
    print(f"\n{'='*70}")
    print(f"Detailed Feedback:")
    print(f"{'='*70}")
    for feedback in result['feedback']:
        print(f"  {feedback}")
    
    return True


def test_keypoint_names():
    """Test if all keypoint names in config are valid"""
    print("\n" + "="*70)
    print("TEST 3: Keypoint Name Validation")
    print("="*70)
    
    valid_keypoint_names = {
        "nose", "left_eye_inner", "left_eye", "left_eye_outer",
        "right_eye_inner", "right_eye", "right_eye_outer",
        "left_ear", "right_ear", "mouth_left", "mouth_right",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky",
        "left_index", "right_index", "left_thumb", "right_thumb",
        "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel",
        "left_foot_index", "right_foot_index"
    }
    
    pose_id = "Akarna_Dhanurasana_front"
    config = get_pose_config(pose_id)
    
    all_valid = True
    invalid_keypoints = []
    
    # Check required keypoints
    for kp in config.required_keypoints:
        if kp not in valid_keypoint_names:
            all_valid = False
            invalid_keypoints.append(kp)
    
    # Check angle points
    for angle in config.required_angles:
        for point in angle.points:
            if point not in valid_keypoint_names:
                all_valid = False
                if point not in invalid_keypoints:
                    invalid_keypoints.append(point)
    
    if all_valid:
        print("✓ All keypoint names are valid!")
        return True
    else:
        print("✗ Invalid keypoint names found:")
        for kp in invalid_keypoints:
            print(f"  - {kp}")
        print(f"\nValid keypoint names are:")
        for kp in sorted(valid_keypoint_names):
            print(f"  - {kp}")
        return False


def main():
    print("\n" + "="*70)
    print(" "*15 + "MANUAL ANGLE ACCURACY TEST SUITE")
    print("="*70)
    
    # Test 1: Configuration loading
    test1_passed = test_pose_config()
    
    if not test1_passed:
        print("\n✗ Test 1 failed. Fix configuration before proceeding.")
        return
    
    # Test 3: Keypoint validation
    test3_passed = test_keypoint_names()
    
    if not test3_passed:
        print("\n✗ Test 3 failed. Fix keypoint names before proceeding.")
        return
    
    # Test 2: Image-based testing
    print("\nLooking for test image...")
    possible_paths = [
        "data/reference_poses/images/Akarna_Dhanurasana_front/Akarna_Dhanurasana_image_1.jpg",
        "data/reference_poses/images/Akarna_Dhanurasana_front/Akarna_Dhanurasana_image_1.jpeg",
        "data/reference_poses/images/Akarna_Dhanurasana_front/Akarna_Dhanurasana_image_1.png",
    ]
    
    image_path = None
    for path in possible_paths:
        if Path(path).exists():
            image_path = path
            break
    
    if image_path:
        test2_passed = test_with_image(image_path)
    else:
        print("\n⚠ Warning: Test image not found. Skipping image-based test.")
        print(f"Tried paths:")
        for path in possible_paths:
            print(f"  - {path}")
        test2_passed = None
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Test 1 (Configuration Loading): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Test 3 (Keypoint Validation):   {'✓ PASSED' if test3_passed else '✗ FAILED'}")
    if test2_passed is not None:
        print(f"Test 2 (Image Detection):       {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    else:
        print(f"Test 2 (Image Detection):       ⚠ SKIPPED (no image)")
    
    if test1_passed and test3_passed:
        print("\n🎉 All critical tests passed! Your configuration is ready to use.")
        print("\nNext steps:")
        print("1. Restart your backend server if it's running")
        print("2. Open http://localhost:8000 in your browser")
        print("3. Select 'Akarna Dhanurasana' pose")
        print("4. Start camera and test the live accuracy!")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
