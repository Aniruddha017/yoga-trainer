// Pose overlay for drawing landmarks on canvas

class PoseOverlay {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');
        
        // MediaPipe connection pairs for drawing skeleton
        this.connections = [
            // Face
            [0, 1], [1, 2], [2, 3], [3, 7],
            [0, 4], [4, 5], [5, 6], [6, 8],
            [9, 10],
            
            // Torso
            [11, 12], [11, 23], [12, 24], [23, 24],
            
            // Left arm
            [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
            
            // Right arm
            [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
            
            // Left leg
            [23, 25], [25, 27], [27, 29], [27, 31],
            
            // Right leg
            [24, 26], [26, 28], [28, 30], [28, 32]
        ];
    }

    clear() {
        /**
         * Clear the canvas
         */
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawKeypoints(keypoints, color = '#00FF00', radius = 5) {
        /**
         * Draw keypoints as circles
         * @param {Array} keypoints - Array of keypoint objects with x, y, visibility
         * @param {string} color - Color for keypoints
         * @param {number} radius - Radius of keypoint circles
         */
        this.ctx.fillStyle = color;
        
        keypoints.forEach(kp => {
            if (kp.visibility > 0.5) {
                const x = kp.x * this.canvas.width;
                const y = kp.y * this.canvas.height;
                
                this.ctx.beginPath();
                this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
                this.ctx.fill();
            }
        });
    }

    drawSkeleton(keypoints, color = '#00FF00', lineWidth = 2) {
        /**
         * Draw skeleton connections between keypoints
         * Only draws connections between the 13 allowed keypoints
         * @param {Array} keypoints - Array of keypoint objects
         * @param {string} color - Color for skeleton lines
         * @param {number} lineWidth - Width of skeleton lines
         */
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = lineWidth;
        
        // Define connections using keypoint NAMES instead of indices
        const namedConnections = [
            // Torso
            ['left_shoulder', 'right_shoulder'],
            ['left_shoulder', 'left_hip'],
            ['right_shoulder', 'right_hip'],
            ['left_hip', 'right_hip'],
            
            // Left arm
            ['left_shoulder', 'left_elbow'],
            ['left_elbow', 'left_wrist'],
            
            // Right arm
            ['right_shoulder', 'right_elbow'],
            ['right_elbow', 'right_wrist'],
            
            // Left leg
            ['left_hip', 'left_knee'],
            ['left_knee', 'left_ankle'],
            
            // Right leg
            ['right_hip', 'right_knee'],
            ['right_knee', 'right_ankle']
        ];
        
        // Draw each connection
        namedConnections.forEach(([startName, endName]) => {
            const start = keypoints.find(kp => kp.name === startName);
            const end = keypoints.find(kp => kp.name === endName);
            
            // Only draw if both points exist and are visible
            if (start && end && start.visibility > 0.5 && end.visibility > 0.5) {
                const startX = start.x * this.canvas.width;
                const startY = start.y * this.canvas.height;
                const endX = end.x * this.canvas.width;
                const endY = end.y * this.canvas.height;
                
                this.ctx.beginPath();
                this.ctx.moveTo(startX, startY);
                this.ctx.lineTo(endX, endY);
                this.ctx.stroke();
            }
        });
    }

    drawPose(keypoints, color = '#00FF00') {
        /**
         * Draw complete pose (keypoints + skeleton)
         * @param {Array} keypoints - Array of keypoint objects
         * @param {string} color - Color for pose visualization
         */
        // Show only these 13 specific keypoints (no face details, no finger points)
        const allowedKeypoints = [
            'nose',                                    // 1 face point only
            'left_shoulder', 'right_shoulder',         // shoulders
            'left_elbow', 'right_elbow',               // elbows
            'left_wrist', 'right_wrist',               // wrists (NO finger points)
            'left_hip', 'right_hip',                   // hips
            'left_knee', 'right_knee',                 // knees
            'left_ankle', 'right_ankle'                // ankles
        ];
        
        const filteredKeypoints = keypoints.filter(kp => allowedKeypoints.includes(kp.name));
        
        this.drawSkeleton(filteredKeypoints, color, 3);
        this.drawKeypoints(filteredKeypoints, color, 6);
    }

    drawColorCodedPose(keypoints, jointFeedback = []) {
        /**
         * Draw pose with color-coded joints based on accuracy
         * Only shows 13 specific keypoints: nose, shoulders, elbows, wrists, hips, knees, ankles
         * @param {Array} keypoints - Array of keypoint objects
         * @param {Array} jointFeedback - Feedback for each joint with scores
         */
        // Show only these 13 specific keypoints (no face details, no finger points)
        const allowedKeypoints = [
            'nose',                                    // 1 face point only
            'left_shoulder', 'right_shoulder',         // shoulders
            'left_elbow', 'right_elbow',               // elbows
            'left_wrist', 'right_wrist',               // wrists (NO finger points)
            'left_hip', 'right_hip',                   // hips
            'left_knee', 'right_knee',                 // knees
            'left_ankle', 'right_ankle'                // ankles
        ];
        
        const filteredKeypoints = keypoints.filter(kp => allowedKeypoints.includes(kp.name));
        
        // Create score map
        const scoreMap = {};
        jointFeedback.forEach(feedback => {
            const jointName = feedback.joint_name.toLowerCase().replace(' ', '_');
            scoreMap[jointName] = feedback.score;
        });

        // Draw skeleton with default color
        this.drawSkeleton(filteredKeypoints, '#00FF00', 2);

        // Draw keypoints with color coding
        filteredKeypoints.forEach((kp, index) => {
            if (kp.visibility > 0.5) {
                const x = kp.x * this.canvas.width;
                const y = kp.y * this.canvas.height;
                
                // Determine color based on score
                let color = '#00FF00'; // Green (default)
                const landmarkName = kp.name;
                
                if (landmarkName && scoreMap[landmarkName] !== undefined) {
                    const score = scoreMap[landmarkName];
                    if (score >= 90) {
                        color = '#00FF00'; // Green - Excellent
                    } else if (score >= 75) {
                        color = '#FFFF00'; // Yellow - Good
                    } else if (score >= 50) {
                        color = '#FFA500'; // Orange - Needs adjustment
                    } else {
                        color = '#FF0000'; // Red - Incorrect
                    }
                }
                
                this.ctx.fillStyle = color;
                this.ctx.beginPath();
                this.ctx.arc(x, y, 6, 0, 2 * Math.PI);
                this.ctx.fill();
            }
        });
    }

    drawConfidence(confidence, x = 10, y = 30) {
        /**
         * Draw confidence score on canvas
         * @param {number} confidence - Confidence value (0-1)
         * @param {number} x - X position
         * @param {number} y - Y position
         */
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 3;
        this.ctx.font = 'bold 20px Arial';
        
        const text = `Confidence: ${(confidence * 100).toFixed(1)}%`;
        
        this.ctx.strokeText(text, x, y);
        this.ctx.fillText(text, x, y);
    }

    drawPoseWithAngleColors(keypoints, angleScores = []) {
        /**
         * Draw pose with color-coded angles based on manual angle accuracy
         * Only shows 13 specific keypoints: nose, shoulders, elbows, wrists, hips, knees, ankles
         * @param {Array} keypoints - Array of keypoint objects
         * @param {Array} angleScores - Scores for each angle with color/status
         */
        // Show only these 13 specific keypoints (no face details, no finger points)
        const allowedKeypoints = [
            'nose',                                    // 1 face point only
            'left_shoulder', 'right_shoulder',         // shoulders
            'left_elbow', 'right_elbow',               // elbows
            'left_wrist', 'right_wrist',               // wrists (NO finger points)
            'left_hip', 'right_hip',                   // hips
            'left_knee', 'right_knee',                 // knees
            'left_ankle', 'right_ankle'                // ankles
        ];
        
        const displayKeypoints = keypoints.filter(kp => allowedKeypoints.includes(kp.name));
        
        // Create a map of keypoint names to colors based on angle scores
        const keypointColors = {};
        
        angleScores.forEach(angleScore => {
            // Color the keypoints involved in this angle
            angleScore.points.forEach(pointName => {
                if (!keypointColors[pointName] || angleScore.score > (keypointColors[pointName].score || 0)) {
                    keypointColors[pointName] = {
                        color: angleScore.color,
                        score: angleScore.score
                    };
                }
            });
        });
        
        // Draw colored connections based on angle scores
        angleScores.forEach(angleScore => {
            const [point1Name, vertexName, point2Name] = angleScore.points;
            
            // Find the keypoints
            const point1 = keypoints.find(kp => kp.name === point1Name);
            const vertex = keypoints.find(kp => kp.name === vertexName);
            const point2 = keypoints.find(kp => kp.name === point2Name);
            
            if (point1 && vertex && point2 && 
                point1.visibility > 0.5 && vertex.visibility > 0.5 && point2.visibility > 0.5) {
                
                // Get color based on score
                let lineColor = angleScore.color;
                
                // Draw the two lines that form this angle
                this.ctx.strokeStyle = lineColor;
                this.ctx.lineWidth = 4;
                
                // Line 1: point1 to vertex
                this.ctx.beginPath();
                this.ctx.moveTo(point1.x * this.canvas.width, point1.y * this.canvas.height);
                this.ctx.lineTo(vertex.x * this.canvas.width, vertex.y * this.canvas.height);
                this.ctx.stroke();
                
                // Line 2: vertex to point2
                this.ctx.beginPath();
                this.ctx.moveTo(vertex.x * this.canvas.width, vertex.y * this.canvas.height);
                this.ctx.lineTo(point2.x * this.canvas.width, point2.y * this.canvas.height);
                this.ctx.stroke();
            }
        });
        
        // Draw keypoints with colors (only used keypoints)
        displayKeypoints.forEach(kp => {
            if (kp.visibility > 0.5) {
                const x = kp.x * this.canvas.width;
                const y = kp.y * this.canvas.height;
                
                // Use color from angle scores if available, otherwise default
                let color = keypointColors[kp.name]?.color || '#00FF00';
                
                // Draw outer circle (darker)
                this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                this.ctx.beginPath();
                this.ctx.arc(x, y, 8, 0, 2 * Math.PI);
                this.ctx.fill();
                
                // Draw inner circle (colored)
                this.ctx.fillStyle = color;
                this.ctx.beginPath();
                this.ctx.arc(x, y, 6, 0, 2 * Math.PI);
                this.ctx.fill();
            }
        });
        
        // Draw angle symbols at vertices
        angleScores.forEach(angleScore => {
            const [, vertexName,] = angleScore.points;
            const vertex = keypoints.find(kp => kp.name === vertexName);
            
            if (vertex && vertex.visibility > 0.5) {
                const x = vertex.x * this.canvas.width;
                const y = vertex.y * this.canvas.height;
                
                // Draw angle arc indicator
                this.ctx.strokeStyle = angleScore.color;
                this.ctx.lineWidth = 2;
                this.ctx.beginPath();
                this.ctx.arc(x, y, 15, 0, Math.PI / 4);
                this.ctx.stroke();
                
                // Draw angle value text
                this.ctx.fillStyle = angleScore.color;
                this.ctx.strokeStyle = '#000000';
                this.ctx.lineWidth = 2;
                this.ctx.font = 'bold 12px Arial';
                const angleText = `${angleScore.actual_angle}°`;
                this.ctx.strokeText(angleText, x + 20, y - 10);
                this.ctx.fillText(angleText, x + 20, y - 10);
            }
        });
    }
}

