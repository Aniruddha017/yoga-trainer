// API Client for communicating with FastAPI backend

const API_BASE_URL = 'http://localhost:8000/api/v1';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async detectPose(base64Image) {
        /**
         * Detect pose from base64 encoded image
         * @param {string} base64Image - Base64 encoded image
         * @returns {Promise} Pose detection response
         */
        try {
            const response = await fetch(`${this.baseURL}/pose-detection/detect-pose`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: base64Image })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Pose detection failed');
            }

            return data;
        } catch (error) {
            console.error('Error detecting pose:', error);
            throw error;
        }
    }

    async calculateAccuracy(userKeypoints, referencePoseId) {
        /**
         * Calculate pose accuracy
         * @param {Array} userKeypoints - User's detected keypoints
         * @param {string} referencePoseId - ID of reference pose
         * @returns {Promise} Accuracy calculation response
         */
        try {
            const response = await fetch(`${this.baseURL}/accuracy/calculate-accuracy`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_keypoints: userKeypoints,
                    reference_pose_id: referencePoseId
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Accuracy calculation failed');
            }

            return data;
        } catch (error) {
            console.error('Error calculating accuracy:', error);
            throw error;
        }
    }

    async listReferencePoses() {
        /**
         * Get list of all reference poses
         * @returns {Promise} List of reference poses
         */
        try {
            const response = await fetch(`${this.baseURL}/reference/poses`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to load reference poses');
            }

            return data;
        } catch (error) {
            console.error('Error loading reference poses:', error);
            throw error;
        }
    }

    async getReferencePose(poseId) {
        /**
         * Get detailed information about a specific reference pose
         * @param {string} poseId - ID of the pose
         * @returns {Promise} Reference pose details
         */
        try {
            const response = await fetch(`${this.baseURL}/reference/poses/${poseId}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to load reference pose');
            }

            return data;
        } catch (error) {
            console.error('Error loading reference pose:', error);
            throw error;
        }
    }

    async uploadReferencePose(poseData) {
        /**
         * Upload a new reference pose
         * @param {Object} poseData - Pose data including image and metadata
         * @returns {Promise} Upload response
         */
        try {
            const response = await fetch(`${this.baseURL}/reference/poses/upload`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(poseData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to upload reference pose');
            }

            return data;
        } catch (error) {
            console.error('Error uploading reference pose:', error);
            throw error;
        }
    }

    async healthCheck() {
        /**
         * Check API health status
         * @returns {Promise} Health status
         */
        try {
            const response = await fetch(`${this.baseURL.replace('/api/v1', '')}/api/health`);
            return await response.json();
        } catch (error) {
            console.error('Error checking API health:', error);
            throw error;
        }
    }
}

// Export singleton instance
const apiClient = new APIClient();
