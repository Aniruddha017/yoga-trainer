import numpy as np
from typing import List, Dict, Tuple
from app.models.pose import Keypoint, JointAngles, JointFeedback, AccuracyResult
from app.utils.geometry import calculate_angle, euclidean_distance
from app.utils.keypoint_utils import normalize_keypoints, get_keypoint_by_name
from app.config import settings


class AccuracyCalculator:
    """Calculate pose accuracy by comparing user pose with reference pose"""
    
    def __init__(self):
        """Initialize accuracy calculator"""
        self.angle_weight = settings.angle_weight
        self.distance_weight = settings.distance_weight
        self.angle_penalty = settings.angle_penalty_factor
    
    def calculate_joint_angles(self, keypoints: List[Keypoint]) -> JointAngles:
        """
        Calculate angles at major joints
        
        Args:
            keypoints: List of pose keypoints
            
        Returns:
            JointAngles object with calculated angles
        """
        try:
            # Left elbow: shoulder-elbow-wrist
            left_elbow_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "left_shoulder"),
                get_keypoint_by_name(keypoints, "left_elbow"),
                get_keypoint_by_name(keypoints, "left_wrist")
            )
            
            # Right elbow
            right_elbow_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "right_shoulder"),
                get_keypoint_by_name(keypoints, "right_elbow"),
                get_keypoint_by_name(keypoints, "right_wrist")
            )
            
            # Left shoulder: elbow-shoulder-hip
            left_shoulder_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "left_elbow"),
                get_keypoint_by_name(keypoints, "left_shoulder"),
                get_keypoint_by_name(keypoints, "left_hip")
            )
            
            # Right shoulder
            right_shoulder_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "right_elbow"),
                get_keypoint_by_name(keypoints, "right_shoulder"),
                get_keypoint_by_name(keypoints, "right_hip")
            )
            
            # Left hip: shoulder-hip-knee
            left_hip_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "left_shoulder"),
                get_keypoint_by_name(keypoints, "left_hip"),
                get_keypoint_by_name(keypoints, "left_knee")
            )
            
            # Right hip
            right_hip_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "right_shoulder"),
                get_keypoint_by_name(keypoints, "right_hip"),
                get_keypoint_by_name(keypoints, "right_knee")
            )
            
            # Left knee: hip-knee-ankle
            left_knee_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "left_hip"),
                get_keypoint_by_name(keypoints, "left_knee"),
                get_keypoint_by_name(keypoints, "left_ankle")
            )
            
            # Right knee
            right_knee_angle = calculate_angle(
                get_keypoint_by_name(keypoints, "right_hip"),
                get_keypoint_by_name(keypoints, "right_knee"),
                get_keypoint_by_name(keypoints, "right_ankle")
            )
            
            return JointAngles(
                left_elbow=left_elbow_angle,
                right_elbow=right_elbow_angle,
                left_shoulder=left_shoulder_angle,
                right_shoulder=right_shoulder_angle,
                left_hip=left_hip_angle,
                right_hip=right_hip_angle,
                left_knee=left_knee_angle,
                right_knee=right_knee_angle
            )
        
        except Exception as e:
            print(f"Error calculating joint angles: {e}")
            return JointAngles()
    
    def calculate_angle_similarity(
        self, 
        ref_angles: JointAngles, 
        user_angles: JointAngles
    ) -> Tuple[float, List[JointFeedback]]:
        """
        Calculate angle similarity score
        
        Args:
            ref_angles: Reference pose angles
            user_angles: User pose angles
            
        Returns:
            (score, feedback) tuple
        """
        joint_scores = []
        feedback_list = []
        
        # Compare each joint
        joint_pairs = [
            ("left_elbow", ref_angles.left_elbow, user_angles.left_elbow),
            ("right_elbow", ref_angles.right_elbow, user_angles.right_elbow),
            ("left_shoulder", ref_angles.left_shoulder, user_angles.left_shoulder),
            ("right_shoulder", ref_angles.right_shoulder, user_angles.right_shoulder),
            ("left_hip", ref_angles.left_hip, user_angles.left_hip),
            ("right_hip", ref_angles.right_hip, user_angles.right_hip),
            ("left_knee", ref_angles.left_knee, user_angles.left_knee),
            ("right_knee", ref_angles.right_knee, user_angles.right_knee),
        ]
        
        for joint_name, ref_angle, user_angle in joint_pairs:
            if ref_angle is None or user_angle is None:
                continue
            
            # Calculate angle difference
            angle_diff = abs(ref_angle - user_angle)
            
            # Calculate score (0-100)
            score = max(0, 100 - angle_diff * self.angle_penalty)
            joint_scores.append(score)
            
            # Generate feedback
            if score >= 90:
                message = "Excellent!"
            elif score >= 75:
                message = f"Good, adjust by {angle_diff:.1f}°"
            elif score >= 50:
                message = f"Needs adjustment: {angle_diff:.1f}° off"
            else:
                message = f"Incorrect angle: {angle_diff:.1f}° difference"
            
            feedback_list.append(JointFeedback(
                joint_name=joint_name.replace("_", " ").title(),
                score=round(score, 2),
                angle_difference=round(angle_diff, 2),
                feedback_message=message
            ))
        
        # Average score
        overall_score = np.mean(joint_scores) if joint_scores else 0.0
        
        return overall_score, feedback_list
    
    def calculate_distance_similarity(
        self, 
        ref_keypoints: List[Keypoint], 
        user_keypoints: List[Keypoint]
    ) -> float:
        """
        Calculate keypoint distance similarity
        
        Args:
            ref_keypoints: Normalized reference keypoints
            user_keypoints: Normalized user keypoints
            
        Returns:
            Distance similarity score (0-100)
        """
        if len(ref_keypoints) != len(user_keypoints):
            return 0.0
        
        # Calculate sum of Euclidean distances
        total_distance = 0.0
        valid_points = 0
        
        for ref_kp, user_kp in zip(ref_keypoints, user_keypoints):
            # Only compare visible keypoints
            if ref_kp.visibility > 0.5 and user_kp.visibility > 0.5:
                distance = euclidean_distance(ref_kp, user_kp)
                total_distance += distance
                valid_points += 1
        
        if valid_points == 0:
            return 0.0
        
        # Average distance
        avg_distance = total_distance / valid_points
        
        # Convert to similarity score (exponential decay)
        # Lower distance = higher score
        score = 100 * np.exp(-avg_distance * 10)
        
        return min(100.0, max(0.0, score))
    
    def calculate_accuracy(
        self, 
        reference_keypoints: List[Keypoint], 
        user_keypoints: List[Keypoint]
    ) -> AccuracyResult:
        """
        Calculate overall pose accuracy
        
        Args:
            reference_keypoints: Reference pose keypoints
            user_keypoints: User pose keypoints
            
        Returns:
            AccuracyResult with scores and feedback
        """
        # Normalize both poses
        ref_normalized = normalize_keypoints(reference_keypoints)
        user_normalized = normalize_keypoints(user_keypoints)
        
        # Calculate joint angles
        ref_angles = self.calculate_joint_angles(ref_normalized)
        user_angles = self.calculate_joint_angles(user_normalized)
        
        # Calculate angle similarity
        angle_score, joint_feedback = self.calculate_angle_similarity(ref_angles, user_angles)
        
        # Calculate distance similarity
        distance_score = self.calculate_distance_similarity(ref_normalized, user_normalized)
        
        # Calculate weighted overall score
        overall_accuracy = (
            self.angle_weight * angle_score + 
            self.distance_weight * distance_score
        )
        
        # Generate general feedback
        general_feedback = self._generate_general_feedback(overall_accuracy, joint_feedback)
        
        return AccuracyResult(
            overall_accuracy=round(overall_accuracy, 2),
            angle_score=round(angle_score, 2),
            distance_score=round(distance_score, 2),
            joint_feedback=joint_feedback,
            general_feedback=general_feedback
        )
    
    def _generate_general_feedback(
        self, 
        overall_accuracy: float, 
        joint_feedback: List[JointFeedback]
    ) -> str:
        """Generate general improvement suggestions"""
        if overall_accuracy >= 90:
            return "Excellent pose! Keep it up!"
        elif overall_accuracy >= 75:
            # Find worst performing joint
            worst_joint = min(joint_feedback, key=lambda x: x.score, default=None)
            if worst_joint:
                return f"Good pose! Focus on improving your {worst_joint.joint_name.lower()}."
            return "Good pose! Minor adjustments needed."
        elif overall_accuracy >= 50:
            # Find top 2 worst joints
            sorted_joints = sorted(joint_feedback, key=lambda x: x.score)[:2]
            joint_names = [j.joint_name.lower() for j in sorted_joints]
            return f"Needs improvement. Focus on: {', '.join(joint_names)}."
        else:
            return "Significant adjustments needed. Review the reference pose and try again."


# Singleton instance
_accuracy_calculator_instance: AccuracyCalculator = None


def get_accuracy_calculator() -> AccuracyCalculator:
    """Get singleton accuracy calculator instance"""
    global _accuracy_calculator_instance
    if _accuracy_calculator_instance is None:
        _accuracy_calculator_instance = AccuracyCalculator()
    return _accuracy_calculator_instance
