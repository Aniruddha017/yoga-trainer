"""
Manual accuracy calculator using predefined angles per pose
"""

from typing import List, Dict, Optional
import math
from app.models.pose import Keypoint
from app.config.pose_angles import get_pose_config, AngleDefinition, has_config
from app.utils.geometry import calculate_angle as calc_angle_util


class ManualAccuracyCalculator:
    """Calculate pose accuracy based on manually defined angles"""
    
    def calculate_accuracy(
        self,
        user_keypoints: List[Keypoint],
        pose_id: str,
        reference_keypoints: Optional[List[Keypoint]] = None,
        position_weight: float = 0.2  # 30% position, 70% angles
    ) -> Dict:
        """
        Calculate accuracy using predefined angles for the pose
        
        Args:
            user_keypoints: Detected keypoints from user's camera
            pose_id: ID of the yoga pose (e.g., "Tree_Pose_or_Vrksasana__front")
            
        Returns:
            Dictionary with overall accuracy and per-angle scores
        """
        # Check if this pose has manual configuration
        if not has_config(pose_id):
            return {
                "overall_accuracy": 0.0,
                "error": f"No manual angle configuration found for pose: {pose_id}",
                "angle_scores": [],
                "feedback": [],
                "using_manual_angles": False
            }
        
        # Get the angle configuration for this pose
        pose_config = get_pose_config(pose_id)
        
        # Convert keypoints list to dictionary for easy lookup
        keypoint_dict = {kp.name: kp for kp in user_keypoints if kp.name}
        
        # Validate that all required keypoints are present and visible
        missing_keypoints = []
        low_visibility_keypoints = []
        
        for required_kp in pose_config.required_keypoints:
            if required_kp not in keypoint_dict:
                missing_keypoints.append(required_kp)
            elif keypoint_dict[required_kp].visibility < 0.5:
                low_visibility_keypoints.append(required_kp)
        
        if missing_keypoints:
            return {
                "overall_accuracy": 0.0,
                "error": f"Missing required keypoints: {', '.join(missing_keypoints)}",
                "angle_scores": [],
                "feedback": [f"Cannot detect: {', '.join(missing_keypoints)}"],
                "using_manual_angles": True
            }
        
        # Calculate accuracy for each defined angle
        angle_scores = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for angle_def in pose_config.required_angles:
            try:
                score_info = self._calculate_angle_score(
                    keypoint_dict,
                    angle_def
                )
                angle_scores.append(score_info)
                
                # Weighted scoring
                total_weighted_score += score_info["score"] * angle_def.weight
                total_weight += angle_def.weight
            except Exception as e:
                print(f"Error calculating angle {angle_def.name}: {e}")
                # Skip this angle if calculation fails
                continue
        
        # Calculate connection scores (body part relationships)
        connection_scores = []
        connection_accuracy = 0.0
        
        if pose_config.required_connections:
            print(f"DEBUG: Processing {len(pose_config.required_connections)} connection definitions")
            connection_result = self._calculate_connections(
                keypoint_dict,
                pose_config.required_connections
            )
            connection_scores = connection_result["connection_scores"]
            connection_accuracy = connection_result["overall_connection_score"]
            print(f"DEBUG: Connection result - {len(connection_scores)} scores, accuracy: {connection_accuracy}")
        
        # Calculate overall accuracy
        angle_accuracy = (total_weighted_score / total_weight) if total_weight > 0 else 0.0
        
        # Calculate position matching if reference keypoints provided
        position_accuracy = 0.0
        position_scores = []
        
        if reference_keypoints:
            position_result = self._calculate_position_matching(
                user_keypoints,
                reference_keypoints,
                pose_config.required_keypoints
            )
            position_accuracy = position_result["overall_position_score"]
            position_scores = position_result["keypoint_scores"]
        
        # Combine angle and position accuracy with weights
        if reference_keypoints:
            # If we have connections, include them in the calculation
            if pose_config.required_connections:
                # 50% angles, 20% position, 30% connections
                overall_accuracy = (
                    angle_accuracy * 0.6 + 
                    position_accuracy * 0.25 +
                    connection_accuracy * 0.15
                )
            else:
                # Original: angles + position only
                overall_accuracy = (
                    angle_accuracy * (1 - position_weight) + 
                    position_accuracy * position_weight
                )
        else:
            # No reference keypoints - use angles and connections if available
            if pose_config.required_connections:
                # 70% angles, 30% connections
                overall_accuracy = angle_accuracy * 0.7 + connection_accuracy * 0.3
            else:
                overall_accuracy = angle_accuracy
        
        # Generate feedback
        feedback = self._generate_feedback(angle_scores)
        
        # Generate general feedback based on overall score
        general_feedback = self._generate_general_feedback(overall_accuracy, angle_scores)
        
        # Collect all unique keypoint names used in angles
        used_keypoints = set()
        for angle_def in pose_config.required_angles:
            used_keypoints.update(angle_def.points)
        
        return {
            "overall_accuracy": round(overall_accuracy, 2),
            "angle_accuracy": round(angle_accuracy, 2),
            "position_accuracy": round(position_accuracy, 2) if reference_keypoints else None,
            "connection_accuracy": round(connection_accuracy, 2) if pose_config.required_connections else None,
            "angle_scores": angle_scores,
            "position_scores": position_scores if reference_keypoints else [],
            "connection_scores": connection_scores,
            "feedback": feedback,
            "general_feedback": general_feedback,
            "pose_name": pose_config.pose_name,
            "view": pose_config.view,
            "using_manual_angles": True,
            "using_position_matching": reference_keypoints is not None,
            "using_connections": pose_config.required_connections is not None,
            "used_keypoints": list(used_keypoints),
            "low_visibility_warning": low_visibility_keypoints if low_visibility_keypoints else None
        }
    
    def _calculate_angle_score(
        self,
        keypoint_dict: Dict[str, Keypoint],
        angle_def: AngleDefinition
    ) -> Dict:
        """Calculate score for a single angle"""
        
        # Get the three points that define this angle
        point1_name, vertex_name, point2_name = angle_def.points
        
        point1 = keypoint_dict[point1_name]
        vertex = keypoint_dict[vertex_name]
        point2 = keypoint_dict[point2_name]
        
        # Calculate the actual angle using the utility function
        actual_angle = calc_angle_util(point1, vertex, point2)
        
        # Calculate deviation from target
        deviation = abs(actual_angle - angle_def.target_angle)
        
        # Calculate score based on tolerance
        # Score decreases from 100 to 0 as deviation increases
        if deviation <= angle_def.tolerance:
            # Within tolerance: 85-100% score (linear decrease)
            score = 100 - (deviation / angle_def.tolerance) * 15
        else:
            # Outside tolerance: 0-85% score (steeper decrease)
            excess_deviation = deviation - angle_def.tolerance
            # Decrease from 85 to 0 over the next tolerance range
            score = max(0, 85 - (excess_deviation / angle_def.tolerance) * 85)
        
        # Determine status and color based on score
        if score >= 85:
            status = "excellent"
            color = "green"
            symbol = "✓"
        elif score >= 70:
            status = "good"
            color = "lightgreen"
            symbol = "○"
        elif score >= 50:
            status = "needs_improvement"
            color = "orange"
            symbol = "△"
        else:
            status = "poor"
            color = "red"
            symbol = "✗"
        
        return {
            "angle_name": angle_def.name,
            "target_angle": angle_def.target_angle,
            "actual_angle": round(actual_angle, 1),
            "deviation": round(deviation, 1),
            "tolerance": angle_def.tolerance,
            "score": round(score, 2),
            "status": status,
            "color": color,
            "symbol": symbol,
            "weight": angle_def.weight,
            "points": list(angle_def.points)
        }
    
    def _generate_feedback(self, angle_scores: List[Dict]) -> List[str]:
        """Generate human-readable feedback for each angle"""
        feedback = []
        
        for score_info in angle_scores:
            angle_name = score_info["angle_name"]
            target = score_info["target_angle"]
            actual = score_info["actual_angle"]
            deviation = score_info["deviation"]
            status = score_info["status"]
            symbol = score_info["symbol"]
            
            if status == "excellent":
                feedback.append(f"{symbol} {angle_name}: Perfect! ({actual}°)")
            elif status == "good":
                if actual > target:
                    feedback.append(f"{symbol} {angle_name}: Good. Try decreasing by {deviation:.0f}°")
                else:
                    feedback.append(f"{symbol} {angle_name}: Good. Try increasing by {deviation:.0f}°")
            elif status == "needs_improvement":
                if actual > target:
                    feedback.append(f"{symbol} {angle_name}: Too open. Decrease by {deviation:.0f}°")
                else:
                    feedback.append(f"{symbol} {angle_name}: Too closed. Increase by {deviation:.0f}°")
            else:
                if actual > target:
                    feedback.append(f"{symbol} {angle_name}: Much too open! Decrease by {deviation:.0f}°")
                else:
                    feedback.append(f"{symbol} {angle_name}: Much too closed! Increase by {deviation:.0f}°")
        
        return feedback
    
    def _generate_general_feedback(self, overall_accuracy: float, angle_scores: List[Dict]) -> str:
        """Generate overall feedback message"""
        if overall_accuracy >= 90:
            return "Excellent pose! You've mastered this position! 🌟"
        elif overall_accuracy >= 80:
            return "Great job! Very close to perfect form. Keep it up! 👍"
        elif overall_accuracy >= 70:
            # Find the worst performing angle
            if angle_scores:
                worst = min(angle_scores, key=lambda x: x["score"])
                return f"Good effort! Focus on improving your {worst['angle_name'].lower()}."
            return "Good pose! A few minor adjustments will get you there."
        elif overall_accuracy >= 50:
            # Find top 2 worst angles
            if len(angle_scores) >= 2:
                sorted_angles = sorted(angle_scores, key=lambda x: x["score"])[:2]
                angle_names = [a["angle_name"].lower() for a in sorted_angles]
                return f"Needs work. Focus on: {angle_names[0]} and {angle_names[1]}."
            return "Needs improvement. Check the feedback for specific angles."
        else:
            return "Keep practicing! Review the reference pose and try again. You've got this! 💪"
    
    def _calculate_connections(
        self,
        keypoint_dict: Dict[str, Keypoint],
        connection_definitions: List
    ) -> Dict:
        """
        Calculate scores for body part connections (e.g., hand holds foot)
        
        Args:
            keypoint_dict: Dictionary of keypoints by name
            connection_definitions: List of ConnectionDefinition objects
            
        Returns:
            Dictionary with connection scores
        """
        from app.config.pose_angles import ConnectionDefinition
        
        connection_scores = []
        total_score = 0.0
        total_weight = 0.0
        
        for conn_def in connection_definitions:
            # Get the two keypoints
            if conn_def.point1 not in keypoint_dict or conn_def.point2 not in keypoint_dict:
                print(f"DEBUG: Connection '{conn_def.name}' - keypoints not found")
                # Add placeholder with 0% score
                connection_scores.append({
                    "connection_name": conn_def.name,
                    "point1": conn_def.point1,
                    "point2": conn_def.point2,
                    "distance": 0.0,
                    "max_distance": conn_def.max_distance,
                    "score": 0.0,
                    "status": "not_detected",
                    "color": "gray",
                    "symbol": "?",
                    "weight": conn_def.weight,
                    "message": "Keypoints not detected"
                })
                continue
            
            kp1 = keypoint_dict[conn_def.point1]
            kp2 = keypoint_dict[conn_def.point2]
            
            # Check visibility - very lenient for connections (0.1 instead of 0.5)
            # Connections just need approximate positions for distance checking
            # Even partially visible keypoints can give useful proximity data
            min_visibility = 0.1
            if kp1.visibility < min_visibility or kp2.visibility < min_visibility:
                print(f"DEBUG: Connection '{conn_def.name}' - low visibility: {kp1.visibility:.3f}, {kp2.visibility:.3f}")
                # Add placeholder with 0% score but show visibility issue
                connection_scores.append({
                    "connection_name": conn_def.name,
                    "point1": conn_def.point1,
                    "point2": conn_def.point2,
                    "distance": 0.0,
                    "max_distance": conn_def.max_distance,
                    "score": 0.0,
                    "status": "not_visible",
                    "color": "gray",
                    "symbol": "?",
                    "weight": conn_def.weight,
                    "message": f"Low visibility ({max(kp1.visibility, kp2.visibility):.1%})"
                })
                continue
            
            # Calculate distance
            distance = math.sqrt(
                (kp1.x - kp2.x) ** 2 + 
                (kp1.y - kp2.y) ** 2
            )
            
            print(f"DEBUG: Connection '{conn_def.name}' - distance: {distance:.3f}, max: {conn_def.max_distance}")
            
            # Calculate score based on distance
            # 0 distance = 100%, max_distance = 0%
            score = max(0, 100 * (1 - distance / conn_def.max_distance))
            
            # Determine status
            if score >= 85:
                status = "excellent"
                color = "green"
                symbol = "✓"
            elif score >= 70:
                status = "good"
                color = "lightgreen"
                symbol = "○"
            elif score >= 50:
                status = "needs_improvement"
                color = "orange"
                symbol = "△"
            else:
                status = "poor"
                color = "red"
                symbol = "✗"
            
            connection_scores.append({
                "connection_name": conn_def.name,
                "point1": conn_def.point1,
                "point2": conn_def.point2,
                "distance": round(distance, 3),
                "max_distance": conn_def.max_distance,
                "score": round(score, 1),
                "status": status,
                "color": color,
                "symbol": symbol,
                "weight": conn_def.weight
            })
            
            total_score += score * conn_def.weight
            total_weight += conn_def.weight
        
        overall_score = (total_score / total_weight) if total_weight > 0 else 0.0
        
        return {
            "overall_connection_score": round(overall_score, 2),
            "connection_scores": connection_scores
        }
    
    def _calculate_position_matching(
        self,
        user_keypoints: List[Keypoint],
        reference_keypoints: List[Keypoint],
        required_keypoint_names: List[str]
    ) -> Dict:
        """
        Calculate position matching score between user and reference pose
        
        Args:
            user_keypoints: User's detected keypoints
            reference_keypoints: Reference pose keypoints
            required_keypoint_names: List of keypoint names to check
            
        Returns:
            Dictionary with position matching scores
        """
        print(f"DEBUG Position: user_keypoints={len(user_keypoints)}, reference={len(reference_keypoints)}, required={len(required_keypoint_names)}")
        
        # Convert to dictionaries
        user_dict = {kp.name: kp for kp in user_keypoints if kp.name}
        ref_dict = {kp.name: kp for kp in reference_keypoints if kp.name}
        
        # Normalize keypoints (center and scale)
        user_normalized = self._normalize_keypoints(user_keypoints)
        ref_normalized = self._normalize_keypoints(reference_keypoints)
        
        print(f"DEBUG Position: normalized user={len(user_normalized)}, ref={len(ref_normalized)}")
        
        user_norm_dict = {kp.name: kp for kp in user_normalized if kp.name}
        ref_norm_dict = {kp.name: kp for kp in ref_normalized if kp.name}
        
        keypoint_scores = []
        total_distance = 0.0
        count = 0
        
        for kp_name in required_keypoint_names:
            if kp_name in user_norm_dict and kp_name in ref_norm_dict:
                user_kp = user_norm_dict[kp_name]
                ref_kp = ref_norm_dict[kp_name]
                
                # Skip if visibility too low
                if user_kp.visibility < 0.3:
                    continue
                
                # Calculate Euclidean distance
                distance = math.sqrt(
                    (user_kp.x - ref_kp.x) ** 2 + 
                    (user_kp.y - ref_kp.y) ** 2
                )
                
                # Convert distance to score (0 distance = 100%, higher distance = lower score)
                # Distance of 0.5 (50% of normalized space) = 0% score
                # This is more forgiving for overall body position matching
                max_distance = 0.3
                score = max(0, 100 * (1 - distance / max_distance))
                
                keypoint_scores.append({
                    "keypoint": kp_name,
                    "distance": round(distance, 3),
                    "score": round(score, 1)
                })
                
                total_distance += distance
                count += 1
        
        avg_distance = total_distance / count if count > 0 else 1.0
        overall_score = max(0, 100 * (1 - avg_distance / 0.5))
        
        print(f"DEBUG Position: matched {count} keypoints, avg_distance={avg_distance:.3f}, score={overall_score:.1f}%")
        
        return {
            "overall_position_score": round(overall_score, 2),
            "average_distance": round(avg_distance, 3),
            "keypoint_scores": keypoint_scores
        }
    
    def _normalize_keypoints(self, keypoints: List[Keypoint]) -> List[Keypoint]:
        """
        Normalize keypoints by centering and scaling
        """
        if not keypoints:
            return keypoints
        
        # Find bounding box - use lenient visibility threshold
        xs = [kp.x for kp in keypoints if kp.visibility > 0.3]
        ys = [kp.y for kp in keypoints if kp.visibility > 0.3]
        
        if not xs or not ys:
            return keypoints
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Calculate center and scale
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        scale = max(max_x - min_x, max_y - min_y)
        
        if scale == 0:
            scale = 1.0
        
        # Normalize each keypoint
        normalized = []
        for kp in keypoints:
            normalized.append(Keypoint(
                landmark_id=kp.landmark_id,
                name=kp.name,
                x=(kp.x - center_x) / scale,
                y=(kp.y - center_y) / scale,
                z=kp.z,
                visibility=kp.visibility
            ))
        
        return normalized


# Singleton instance
_manual_accuracy_calculator_instance: Optional[ManualAccuracyCalculator] = None


def get_manual_accuracy_calculator() -> ManualAccuracyCalculator:
    """Get singleton manual accuracy calculator instance"""
    global _manual_accuracy_calculator_instance
    if _manual_accuracy_calculator_instance is None:
        _manual_accuracy_calculator_instance = ManualAccuracyCalculator()
    return _manual_accuracy_calculator_instance


