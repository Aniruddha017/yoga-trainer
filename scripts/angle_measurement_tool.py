"""
Interactive tool to measure angles in yoga pose images
Click 3 points to measure an angle: point1 → vertex → point2
"""

import cv2
import numpy as np
from pathlib import Path
import json
import sys


class AngleMeasurementTool:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(str(image_path))
        
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Resize if image is too large
        height, width = self.image.shape[:2]
        max_dimension = 1200
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            self.image = cv2.resize(self.image, (new_width, new_height))
            print(f"Image resized to {new_width}x{new_height} for better display")
        
        self.display_image = self.image.copy()
        self.points = []
        self.angles_measured = []
        self.point_labels = ["Point 1 (First Line Start)", "Vertex (Corner)", "Point 2 (Second Line End)"]
        
        # Create window
        cv2.namedWindow('Angle Measurement Tool', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Angle Measurement Tool', self.mouse_callback)
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            
            point_num = len(self.points)
            print(f"✓ {self.point_labels[point_num - 1]}: ({x}, {y})")
            
            # Draw point with number
            color = [(0, 255, 0), (255, 0, 0), (0, 0, 255)][point_num - 1]
            cv2.circle(self.display_image, (x, y), 7, color, -1)
            cv2.putText(self.display_image, str(point_num), (x + 10, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # If we have 3 points, calculate angle
            if len(self.points) == 3:
                print("\nCalculating angle...")
                self.calculate_and_draw_angle()
                
            cv2.imshow('Angle Measurement Tool', self.display_image)
    
    def calculate_angle(self, p1, vertex, p2):
        """Calculate angle between three points in degrees"""
        # Convert to numpy arrays
        p1 = np.array(p1, dtype=np.float64)
        vertex = np.array(vertex, dtype=np.float64)
        p2 = np.array(p2, dtype=np.float64)
        
        # Calculate vectors
        v1 = p1 - vertex
        v2 = p2 - vertex
        
        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        
        return np.degrees(angle)
    
    def calculate_and_draw_angle(self):
        """Calculate angle from 3 points and draw it"""
        p1, vertex, p2 = self.points
        
        # Calculate angle
        angle = self.calculate_angle(p1, vertex, p2)
        
        # Draw lines
        cv2.line(self.display_image, p1, vertex, (255, 255, 0), 3)
        cv2.line(self.display_image, vertex, p2, (255, 255, 0), 3)
        
        # Draw angle arc
        self.draw_angle_arc(p1, vertex, p2, angle)
        
        # Display angle value near vertex
        text = f"{angle:.1f} degrees"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = vertex[0] + 25
        text_y = vertex[1] - 25
        
        # Draw background rectangle for text
        cv2.rectangle(self.display_image, 
                     (text_x - 5, text_y - text_size[1] - 5),
                     (text_x + text_size[0] + 5, text_y + 5),
                     (0, 0, 0), -1)
        
        cv2.putText(self.display_image, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        cv2.imshow('Angle Measurement Tool', self.display_image)
        
        # Ask for angle name
        print(f"\n{'='*60}")
        print(f"✓ ANGLE MEASURED: {angle:.1f}°")
        print(f"{'='*60}")
        print("\nExamples of angle names:")
        print("  - Standing Leg (Right Knee)")
        print("  - Bent Knee (Left)")
        print("  - Arms Overhead")
        print("  - Hip Angle")
        print("  - Torso Alignment")
        
        angle_name = input("\n→ Enter name for this angle: ").strip()
        
        if not angle_name:
            angle_name = f"Angle_{len(self.angles_measured) + 1}"
        
        # Ask for tolerance
        print(f"\nDefault tolerance: 15.0 degrees")
        tolerance_input = input("→ Enter custom tolerance (or press Enter for default): ").strip()
        tolerance = float(tolerance_input) if tolerance_input else 15.0
        
        # Ask for weight
        print(f"\nDefault weight: 1.0 (higher = more important)")
        weight_input = input("→ Enter custom weight (or press Enter for default): ").strip()
        weight = float(weight_input) if weight_input else 1.0
        
        # Save measurement
        self.angles_measured.append({
            "name": angle_name,
            "target_angle": round(angle, 1),
            "tolerance": tolerance,
            "weight": weight,
            "points": [
                {"x": p1[0], "y": p1[1]},
                {"x": vertex[0], "y": vertex[1]},
                {"x": p2[0], "y": p2[1]}
            ]
        })
        
        print(f"\n✓ Saved: {angle_name} = {angle:.1f}° (tolerance: ±{tolerance}°, weight: {weight})")
        print(f"Total angles measured: {len(self.angles_measured)}")
        print("\nReady for next angle. Click 3 points or press 's' to save all.")
        
        # Reset for next measurement
        self.points = []
        self.display_image = self.image.copy()
        
        # Redraw all previous angles
        self.redraw_all_angles()
    
    def draw_angle_arc(self, p1, vertex, p2, angle):
        """Draw an arc showing the angle"""
        # Calculate vectors
        v1 = np.array(p1, dtype=np.float64) - np.array(vertex, dtype=np.float64)
        v2 = np.array(p2, dtype=np.float64) - np.array(vertex, dtype=np.float64)
        
        # Calculate start and end angles for arc
        angle1 = np.degrees(np.arctan2(v1[1], v1[0]))
        angle2 = np.degrees(np.arctan2(v2[1], v2[0]))
        
        # Ensure we draw the smaller arc
        if abs(angle2 - angle1) > 180:
            if angle2 > angle1:
                angle1 += 360
            else:
                angle2 += 360
        
        # Draw arc
        radius = 50
        try:
            cv2.ellipse(self.display_image, vertex, (radius, radius), 0,
                       angle1, angle2, (255, 255, 0), 2)
        except:
            pass  # Skip if arc drawing fails
    
    def redraw_all_angles(self):
        """Redraw all previously measured angles"""
        for idx, measurement in enumerate(self.angles_measured):
            p1 = (measurement["points"][0]["x"], measurement["points"][0]["y"])
            vertex = (measurement["points"][1]["x"], measurement["points"][1]["y"])
            p2 = (measurement["points"][2]["x"], measurement["points"][2]["y"])
            
            # Draw points
            cv2.circle(self.display_image, p1, 5, (0, 200, 0), -1)
            cv2.circle(self.display_image, vertex, 5, (200, 0, 0), -1)
            cv2.circle(self.display_image, p2, 5, (0, 0, 200), -1)
            
            # Draw lines (thinner for previous angles)
            cv2.line(self.display_image, p1, vertex, (150, 150, 0), 1)
            cv2.line(self.display_image, vertex, p2, (150, 150, 0), 1)
            
            # Draw angle text
            cv2.putText(self.display_image, 
                       f"{idx+1}: {measurement['target_angle']}°",
                       (vertex[0] + 15, vertex[1] - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run(self):
        """Run the measurement tool"""
        print("\n" + "=" * 70)
        print(" " * 15 + "YOGA POSE ANGLE MEASUREMENT TOOL")
        print("=" * 70)
        print("\n📐 INSTRUCTIONS:")
        print("-" * 70)
        print("1. Click 3 points to measure an angle:")
        print("   • Point 1: Start of first line (e.g., hip)")
        print("   • Vertex: Corner/joint point (e.g., knee)")
        print("   • Point 2: End of second line (e.g., ankle)")
        print()
        print("2. After clicking 3 points:")
        print("   • Angle will be calculated automatically")
        print("   • Enter a descriptive name for the angle")
        print("   • Optionally set tolerance and weight")
        print()
        print("⌨️  KEYBOARD COMMANDS:")
        print("-" * 70)
        print("  'r' - Reset current 3 points (before completion)")
        print("  's' - Save all measurements to JSON file")
        print("  'q' - Quit the tool")
        print("=" * 70)
        print("\nImage loaded successfully. Click on the image to start measuring!")
        print()
        
        while True:
            cv2.imshow('Angle Measurement Tool', self.display_image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Exiting tool...")
                break
            elif key == ord('r'):
                # Reset current points
                if len(self.points) > 0:
                    self.points = []
                    self.display_image = self.image.copy()
                    self.redraw_all_angles()
                    print("\n↺ Reset current points")
                else:
                    print("\n⚠ No points to reset")
            elif key == ord('s'):
                # Save measurements
                if len(self.angles_measured) > 0:
                    self.save_measurements()
                else:
                    print("\n⚠ No angles measured yet. Measure at least one angle before saving.")
        
        cv2.destroyAllWindows()
    
    def save_measurements(self):
        """Save angle measurements to JSON file"""
        image_stem = Path(self.image_path).stem
        output_dir = Path(self.image_path).parent
        
        # Save measurements JSON
        output_path = output_dir / f"{image_stem}_angles.json"
        
        data = {
            "image": str(self.image_path),
            "total_angles": len(self.angles_measured),
            "measurements": self.angles_measured
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, indent=2, fp=f)
        
        print("\n" + "=" * 70)
        print("✅ MEASUREMENTS SAVED!")
        print("=" * 70)
        print(f"📄 JSON file: {output_path}")
        
        # Save annotated image
        annotated_image_path = output_dir / f"{image_stem}_annotated.jpg"
        cv2.imwrite(str(annotated_image_path), self.display_image)
        print(f"🖼️  Annotated image: {annotated_image_path}")
        
        # Print Python code snippet for pose_angles.py
        print("\n" + "=" * 70)
        print("📋 COPY THIS TO pose_angles.py:")
        print("=" * 70)
        print("\nrequired_angles=[")
        for measurement in self.angles_measured:
            # Try to map to keypoint names (simplified)
            print(f"    AngleDefinition(")
            print(f"        name=\"{measurement['name']}\",")
            print(f"        points=(\"point1_name\", \"vertex_name\", \"point2_name\"),  # TODO: Update with actual keypoint names")
            print(f"        target_angle={measurement['target_angle']},")
            print(f"        tolerance={measurement['tolerance']},")
            print(f"        weight={measurement['weight']}")
            print(f"    ),")
        print("]")
        print("\n" + "=" * 70)
        print(f"\n✓ Total angles measured: {len(self.angles_measured)}")
        print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("\n" + "=" * 70)
        print("Usage: python angle_measurement_tool.py <image_path>")
        print("=" * 70)
        print("\nExample:")
        print('  python scripts/angle_measurement_tool.py "data/reference_poses/images/Tree_Pose__front/tree.jpg"')
        print()
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"\n❌ Error: Image not found: {image_path}")
        sys.exit(1)
    
    try:
        tool = AngleMeasurementTool(image_path)
        tool.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
