// Main application logic

let camera;
let poseOverlay;
let selectedPoseId = null;
let selectedBasePoseName = null;
let currentPoseData = null;  // Store current pose with view info
let currentPose = null;
let lastAccuracyData = null;  // Store last accuracy calculation result
let isLiveAccuracyActive = false;
let lastAccuracyCheckTime = 0;
const ACCURACY_CHECK_INTERVAL = 500; // Check accuracy every 500ms
let animationFrameId = null;

// Smoothing for stable display
let smoothedKeypoints = null;  // Smoothed keypoints to reduce jitter
let smoothedAccuracy = null;   // Smoothed accuracy score
const SMOOTHING_FACTOR = 0.9;  // Lower = more smoothing, higher = faster response (0.5 = 50% new, 50% old)
const MIN_CONFIDENCE_THRESHOLD = 0.5;  // Only update if pose confidence is good

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Yoga Pose Accuracy App...');
    
    // Initialize camera and overlay
    const videoElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('poseCanvas');
    
    camera = new CameraManager(videoElement, canvasElement);
    poseOverlay = new PoseOverlay(canvasElement);
    
    // Load reference poses
    await loadReferencePoses();
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('App initialized successfully');
});

async function loadReferencePoses() {
    /**
     * Load list of reference poses from API
     */
    try {
        const response = await apiClient.listReferencePoses();
        
        if (response.success && response.poses.length > 0) {
            populatePoseSelector(response.poses);
        } else {
            showNotification('No reference poses found. Please add reference poses first.', 'warning');
        }
    } catch (error) {
        console.error('Error loading reference poses:', error);
        showNotification('Failed to load reference poses', 'error');
    }
}

function populatePoseSelector(poses) {
    /**
     * Populate pose selector dropdown with grouped poses
     */
    const selector = document.getElementById('poseSelector');
    selector.innerHTML = '<option value="">Select a yoga pose...</option>';
    
    poses.forEach(pose => {
        const option = document.createElement('option');
        option.value = pose.base_pose_name;
        option.dataset.poseid = pose.pose_id;
        option.dataset.hasfront = pose.has_front;
        option.dataset.hasside = pose.has_side;
        
        // Show available views in the name
        let viewInfo = '';
        if (pose.has_front && pose.has_side) {
            viewInfo = ' (Front & Side views)';
        } else if (pose.has_front) {
            viewInfo = ' (Front view only)';
        } else if (pose.has_side) {
            viewInfo = ' (Side view only)';
        }
        
        option.textContent = `${pose.name} (${pose.difficulty})${viewInfo}`;
        selector.appendChild(option);
    });
    
    selector.disabled = false;
}

function setupEventListeners() {
    /**
     * Setup all event listeners
     */
    // Camera controls
    document.getElementById('startCameraBtn').addEventListener('click', startCamera);
    document.getElementById('stopCameraBtn').addEventListener('click', stopCamera);
    
    // Pose selector
    document.getElementById('poseSelector').addEventListener('change', onPoseSelected);
    
    // View selector
    document.getElementById('viewSelector').addEventListener('change', onViewSelected);
}

async function startCamera() {
    /**
     * Start camera stream and begin live accuracy checking
     */
    try {
        // Reset smoothing variables
        smoothedKeypoints = null;
        smoothedAccuracy = null;
        currentPose = null;
        lastAccuracyData = null;
        
        showLoading('Starting camera...');
        await camera.start();
        
        document.getElementById('startCameraBtn').disabled = true;
        document.getElementById('stopCameraBtn').disabled = false;
        document.getElementById('cameraStatus').textContent = 'Camera active - Live accuracy enabled';
        document.getElementById('cameraStatus').className = 'status-message status-active';
        
        hideLoading();
        
        // Start live accuracy checking
        if (selectedPoseId) {
            startLiveAccuracy();
        }
    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

function stopCamera() {
    /**
     * Stop camera stream and live accuracy checking
     */
    stopLiveAccuracy();
    camera.stop();
    poseOverlay.clear();
    
    // Clear smoothing variables
    smoothedKeypoints = null;
    smoothedAccuracy = null;
    currentPose = null;
    lastAccuracyData = null;
    
    document.getElementById('startCameraBtn').disabled = false;
    document.getElementById('stopCameraBtn').disabled = true;
    document.getElementById('cameraStatus').textContent = 'Camera stopped';
    document.getElementById('cameraStatus').className = 'status-message';
}

function startLiveAccuracy() {
    /**
     * Start continuous pose detection and accuracy calculation
     */
    if (!selectedPoseId) {
        return;
    }
    
    isLiveAccuracyActive = true;
    checkPoseContinuously();
}

function stopLiveAccuracy() {
    /**
     * Stop continuous pose checking
     */
    isLiveAccuracyActive = false;
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

async function checkPoseContinuously() {
    /**
     * Continuously draw pose overlay and check accuracy
     * Drawing happens every frame (60fps) for smooth display
     * Accuracy calculation happens every 500ms to avoid overwhelming API
     */
    if (!isLiveAccuracyActive || !selectedPoseId) {
        return;
    }
    
    // Always draw video frame to prevent external drawings from persisting
    camera.drawVideoToCanvas();
    
    // Redraw the current pose if available (using SMOOTHED keypoints)
    const keypointsToShow = smoothedKeypoints || currentPose?.keypoints;
    
    if (keypointsToShow) {
        if (lastAccuracyData) {
            // Draw with accuracy coloring
            if (lastAccuracyData.type === 'manual') {
                poseOverlay.drawPoseWithAngleColors(
                    keypointsToShow,
                    lastAccuracyData.angle_scores
                );
            } else if (lastAccuracyData.type === 'standard') {
                poseOverlay.drawColorCodedPose(
                    keypointsToShow,
                    lastAccuracyData.joint_feedback
                );
            } else {
                poseOverlay.drawPose(keypointsToShow, '#00FF00');
            }
        } else {
            // No accuracy data yet, just draw basic pose
            poseOverlay.drawPose(keypointsToShow, '#00FF00');
        }
        
        if (currentPose) {
            poseOverlay.drawConfidence(currentPose.confidence);
        }
    }
    
    const now = Date.now();
    
    // Throttle accuracy checks to avoid overwhelming the API
    if (now - lastAccuracyCheckTime >= ACCURACY_CHECK_INTERVAL) {
        lastAccuracyCheckTime = now;
        await detectAndCalculateAccuracy();
    }
    
    // Schedule next frame (this runs at ~60fps for smooth drawing)
    animationFrameId = requestAnimationFrame(checkPoseContinuously);
}

function smoothKeypoints(newKeypoints, oldKeypoints, smoothingFactor) {
    /**
     * Smooth keypoint positions to reduce jitter
     * @param {Array} newKeypoints - Latest detected keypoints
     * @param {Array} oldKeypoints - Previous smoothed keypoints
     * @param {number} smoothingFactor - 0-1, lower = more smoothing
     * @returns {Array} Smoothed keypoints
     */
    if (!oldKeypoints || oldKeypoints.length === 0) {
        return newKeypoints;
    }
    
    return newKeypoints.map((newKp, index) => {
        const oldKp = oldKeypoints[index];
        if (!oldKp) return newKp;
        
        return {
            ...newKp,
            x: oldKp.x + (newKp.x - oldKp.x) * smoothingFactor,
            y: oldKp.y + (newKp.y - oldKp.y) * smoothingFactor,
            visibility: Math.max(oldKp.visibility, newKp.visibility) // Keep higher visibility
        };
    });
}

function smoothAccuracyScore(newScore, oldScore, smoothingFactor) {
    /**
     * Smooth accuracy score to prevent sudden jumps
     * @param {number} newScore - Latest accuracy score
     * @param {number} oldScore - Previous smoothed score
     * @param {number} smoothingFactor - 0-1, lower = more smoothing
     * @returns {number} Smoothed score
     */
    if (oldScore === null || oldScore === undefined) {
        return newScore;
    }
    
    return oldScore + (newScore - oldScore) * smoothingFactor;
}

async function detectAndCalculateAccuracy() {
    /**
     * Detect pose and calculate accuracy using manual angles
     */
    if (!selectedPoseId) {
        return;
    }
    
    try {
        // Capture frame
        const imageData = camera.captureFrame();
        if (!imageData) {
            return;
        }
        
        // Detect pose
        const detectionResponse = await apiClient.detectPose(imageData);
        
        if (!detectionResponse.success || !detectionResponse.pose) {
            // No pose detected - don't immediately clear, keep last good pose briefly
            if (currentPose && currentPose.confidence < MIN_CONFIDENCE_THRESHOLD) {
                currentPose = null;
                smoothedKeypoints = null;
                lastAccuracyData = null;
            }
            return;
        }
        
        const detectedPose = detectionResponse.pose;
        
        // Only update if confidence is good enough
        if (detectedPose.confidence >= MIN_CONFIDENCE_THRESHOLD) {
            // Smooth keypoints to reduce jitter
            smoothedKeypoints = smoothKeypoints(
                detectedPose.keypoints,
                smoothedKeypoints,
                SMOOTHING_FACTOR
            );
            
            currentPose = {
                keypoints: detectedPose.keypoints, // Keep original for API
                confidence: detectedPose.confidence
            };
        } else {
            // Low confidence - keep previous pose
            return;
        }
        
        // Try manual accuracy first
        try {
            const manualAccuracyResponse = await fetch('/api/v1/manual-accuracy/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_keypoints: currentPose.keypoints,
                    pose_id: selectedPoseId
                })
            });
            
            if (manualAccuracyResponse.ok) {
                const manualData = await manualAccuracyResponse.json();
                
                if (manualData.success && manualData.data.using_manual_angles) {
                    // Smooth the accuracy score
                    const newAccuracy = manualData.data.overall_accuracy;
                    const displayAccuracy = smoothAccuracyScore(
                        newAccuracy,
                        smoothedAccuracy,
                        SMOOTHING_FACTOR
                    );
                    smoothedAccuracy = displayAccuracy;
                    
                    // Store manual angle-based accuracy data with smoothed score
                    lastAccuracyData = {
                        type: 'manual',
                        ...manualData.data  // Store all fields including connection_scores
                    };
                    
                    // Update displayed accuracy with smoothed value
                    const smoothedData = {
                        ...manualData.data,
                        overall_accuracy: displayAccuracy
                    };
                    
                    // Debug log to verify connection data
                    if (smoothedData.connection_scores && smoothedData.connection_scores.length > 0) {
                        console.log('Connection scores:', smoothedData.connection_scores);
                    }
                    
                    displayManualAccuracyResults(smoothedData);
                    return; // Drawing happens in the main loop
                }
            }
        } catch (manualError) {
            console.log('Manual accuracy not available, falling back to standard calculation');
        }
        
        // Fallback to standard accuracy calculation
        const accuracyResponse = await apiClient.calculateAccuracy(
            currentPose.keypoints,
            selectedPoseId
        );
        
        if (accuracyResponse.success) {
            // Smooth the accuracy score
            const newAccuracy = accuracyResponse.accuracy.overall_accuracy;
            const displayAccuracy = smoothAccuracyScore(
                newAccuracy,
                smoothedAccuracy,
                SMOOTHING_FACTOR
            );
            smoothedAccuracy = displayAccuracy;
            
            // Store standard accuracy data
            lastAccuracyData = {
                type: 'standard',
                joint_feedback: accuracyResponse.accuracy.joint_feedback
            };
            
            // Update displayed accuracy with smoothed value
            const smoothedAccuracyData = {
                ...accuracyResponse.accuracy,
                overall_accuracy: displayAccuracy
            };
            displayAccuracyResults(smoothedAccuracyData);
        } else {
            // Just basic pose data
            lastAccuracyData = {
                type: 'basic'
            };
        }
        // Drawing happens in the main loop at 60fps
    } catch (error) {
        console.error('Error in live accuracy check:', error);
        // Don't show alert during live checking, just log
    }
}

async function onPoseSelected(event) {
    /**
     * Handle pose selection change - populate view selector
     */
    selectedBasePoseName = event.target.value;
    const selectedOption = event.target.selectedOptions[0];
    
    const viewSelector = document.getElementById('viewSelector');
    viewSelector.innerHTML = '<option value="">Select view...</option>';
    
    if (!selectedBasePoseName) {
        viewSelector.disabled = true;
        selectedPoseId = null;
        document.getElementById('referenceImage').style.display = 'none';
        document.getElementById('referencePlaceholder').style.display = 'block';
        document.getElementById('poseDescription').textContent = '';
        return;
    }
    
    // Get available views
    const hasFront = selectedOption.dataset.hasfront === 'true';
    const hasSide = selectedOption.dataset.hasside === 'true';
    
    if (hasFront) {
        const option = document.createElement('option');
        option.value = 'front';
        option.textContent = 'Front View';
        viewSelector.appendChild(option);
    }
    
    if (hasSide) {
        const option = document.createElement('option');
        option.value = 'side';
        option.textContent = 'Side View';
        viewSelector.appendChild(option);
    }
    
    viewSelector.disabled = false;
    
    // Auto-select front view if available, otherwise side
    if (hasFront) {
        viewSelector.value = 'front';
        selectedPoseId = `${selectedBasePoseName}_front`;
    } else if (hasSide) {
        viewSelector.value = 'side';
        selectedPoseId = `${selectedBasePoseName}_side`;
    }
    
    // Load the selected view
    await loadPoseView(selectedPoseId);
}

async function onViewSelected(event) {
    /**
     * Handle view selection change
     */
    const view = event.target.value;
    
    if (!view || !selectedBasePoseName) {
        return;
    }
    
    selectedPoseId = `${selectedBasePoseName}_${view}`;
    await loadPoseView(selectedPoseId);
}

async function loadPoseView(poseId) {
    /**
     * Load and display the selected pose view
     */
    if (!poseId) return;
    
    try {
        const response = await apiClient.getReferencePose(poseId);
        
        if (response.success && response.pose) {
            const pose = response.pose;
            currentPoseData = pose;
            
            // Display reference image
            if (pose.thumbnail) {
                document.getElementById('referenceImage').src = pose.thumbnail;
                document.getElementById('referenceImage').style.display = 'block';
                document.getElementById('referencePlaceholder').style.display = 'none';
            }
            
            // Display description
            const viewText = pose.view_angle === 'front' ? 'Front View' : 'Side View';
            const description = pose.description || `${pose.name} - ${viewText}`;
            document.getElementById('poseDescription').innerHTML = `
                <strong>${pose.name}</strong><br>
                <span style="color: #667eea;">${viewText}</span><br>
                ${pose.description ? pose.description : ''}
            `;
            
            // Restart live accuracy if camera is active
            if (camera && camera.stream) {
                stopLiveAccuracy();
                startLiveAccuracy();
            }
        }
    } catch (error) {
        console.error('Error loading pose view:', error);
        alert(`Error: Failed to load pose view`);
    }
}

function displayAccuracyResults(accuracy) {
    /**
     * Display standard accuracy results on the page
     */
    // Show results section
    document.getElementById('resultsContainer').classList.remove('results-hidden');
    document.getElementById('resultsPlaceholder').style.display = 'none';
    
    // Overall accuracy
    const overallElem = document.getElementById('overallAccuracy');
    overallElem.textContent = accuracy.overall_accuracy.toFixed(1);
    overallElem.className = 'accuracy-value ' + getAccuracyClass(accuracy.overall_accuracy);
    
    // Score breakdown
    document.getElementById('angleScore').textContent = `${accuracy.angle_score.toFixed(1)}%`;
    document.getElementById('distanceScore').textContent = `${accuracy.distance_score.toFixed(1)}%`;
    
    // General feedback
    document.getElementById('generalFeedback').textContent = accuracy.general_feedback;
    
    // Joint feedback
    const jointFeedbackContainer = document.getElementById('jointFeedback');
    jointFeedbackContainer.innerHTML = '';
    
    accuracy.joint_feedback.forEach(feedback => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'joint-item ' + getScoreClass(feedback.score);
        feedbackItem.innerHTML = `
            <div class="joint-name">${feedback.joint_name}</div>
            <div class="joint-score">${feedback.score.toFixed(1)}%</div>
            <div class="joint-message">${feedback.feedback_message}</div>
        `;
        jointFeedbackContainer.appendChild(feedbackItem);
    });
}

function displayManualAccuracyResults(data) {
    /**
     * Display manual angle-based accuracy results with position matching
     */
    // Show results section
    document.getElementById('resultsContainer').classList.remove('results-hidden');
    document.getElementById('resultsPlaceholder').style.display = 'none';
    
    // Overall accuracy
    const overallElem = document.getElementById('overallAccuracy');
    overallElem.textContent = data.overall_accuracy.toFixed(1);
    overallElem.className = 'accuracy-value ' + getAccuracyClass(data.overall_accuracy);
    
    // Update breakdown to show both angle and position scores
    if (data.using_position_matching && data.position_accuracy !== null) {
        document.getElementById('angleScore').textContent = `${data.angle_accuracy.toFixed(1)}% (Angles)`;
        document.getElementById('distanceScore').textContent = `${data.position_accuracy.toFixed(1)}% (Position)`;
    } else if (data.using_connections && data.connection_accuracy !== null) {
        document.getElementById('angleScore').textContent = `${data.angle_accuracy.toFixed(1)}% (Angles)`;
        document.getElementById('distanceScore').textContent = `${data.connection_accuracy.toFixed(1)}% (Connections)`;
    } else {
        document.getElementById('angleScore').textContent = `${data.overall_accuracy.toFixed(1)}% (Angles Only)`;
        document.getElementById('distanceScore').textContent = 'N/A';
    }
    
    // General feedback
    document.getElementById('generalFeedback').textContent = data.general_feedback;
    
    // Angle-specific feedback - only rebuild if structure changed
    const jointFeedbackContainer = document.getElementById('jointFeedback');
    const needsRebuild = shouldRebuildFeedback(data);
    
    if (needsRebuild) {
        // Full rebuild when structure changes
        jointFeedbackContainer.innerHTML = '';
        buildFeedbackContainer(data, jointFeedbackContainer);
    } else {
        // Just update values for smooth display
        updateFeedbackValues(data, jointFeedbackContainer);
    }
}

// Track last feedback structure to detect changes
let lastFeedbackStructure = null;

function shouldRebuildFeedback(data) {
    /**
     * Check if feedback structure changed (number of angles/connections)
     */
    const currentStructure = {
        angleCount: data.angle_scores ? data.angle_scores.length : 0,
        connectionCount: data.connection_scores ? data.connection_scores.length : 0,
        hasConnections: data.using_connections || false
    };
    
    // Debug log
    console.log('Current structure:', currentStructure);
    console.log('Last structure:', lastFeedbackStructure);
    
    if (!lastFeedbackStructure ||
        lastFeedbackStructure.angleCount !== currentStructure.angleCount ||
        lastFeedbackStructure.connectionCount !== currentStructure.connectionCount ||
        lastFeedbackStructure.hasConnections !== currentStructure.hasConnections) {
        lastFeedbackStructure = currentStructure;
        console.log('Structure changed - rebuilding');
        return true;
    }
    
    console.log('Structure unchanged - updating values');
    return false;
}

function buildFeedbackContainer(data, container) {
    /**
     * Build the complete feedback container structure
     */
    console.log('Building feedback container with data:', {
        angleCount: data.angle_scores?.length,
        connectionCount: data.connection_scores?.length,
        hasConnections: data.using_connections
    });
    
    container.innerHTML = '';
    
    // Add angle scores
    data.angle_scores.forEach((angleScore, index) => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'joint-item angle-item-' + angleScore.status;
        feedbackItem.dataset.type = 'angle';
        feedbackItem.dataset.index = index;
        feedbackItem.innerHTML = `
            <div class="joint-name">
                <span class="angle-symbol" style="color: ${angleScore.color}">${angleScore.symbol}</span>
                ${angleScore.angle_name}
            </div>
            <div class="joint-score" style="color: ${angleScore.color}">
                ${angleScore.score.toFixed(1)}%
            </div>
            <div class="joint-message">
                ${angleScore.actual_angle}° (target: ${angleScore.target_angle}°, off by ${angleScore.deviation}°)
            </div>
        `;
        container.appendChild(feedbackItem);
    });
    
    // Add connection scores if this pose uses connections
    if (data.using_connections) {
        // Add separator
        const separator = document.createElement('div');
        separator.style.margin = '15px 0';
        separator.style.borderTop = '1px solid #ddd';
        separator.dataset.type = 'separator';
        container.appendChild(separator);
        
        // Add connections header
        const connectionsHeader = document.createElement('h4');
        connectionsHeader.textContent = 'Body Part Connections';
        connectionsHeader.style.marginTop = '10px';
        connectionsHeader.dataset.type = 'header';
        container.appendChild(connectionsHeader);
        
        // Always show connections if defined for this pose
        if (data.connection_scores && data.connection_scores.length > 0) {
            data.connection_scores.forEach((conn, index) => {
                const feedbackItem = document.createElement('div');
                feedbackItem.className = 'joint-item angle-item-' + conn.status;
                feedbackItem.dataset.type = 'connection';
                feedbackItem.dataset.index = index;
                
                // Use custom message if available (for not detected/low visibility)
                const message = conn.message || 
                    `Distance: ${(conn.distance * 100).toFixed(1)}% (max: ${(conn.max_distance * 100).toFixed(0)}%)`;
                
                feedbackItem.innerHTML = `
                    <div class="joint-name">
                        <span class="angle-symbol" style="color: ${conn.color}">${conn.symbol}</span>
                        ${conn.connection_name}
                    </div>
                    <div class="joint-score" style="color: ${conn.color}">
                        ${conn.score.toFixed(1)}%
                    </div>
                    <div class="joint-message">
                        ${message}
                    </div>
                `;
                container.appendChild(feedbackItem);
            });
        } else {
            // Show placeholder when no connection data yet
            const placeholder = document.createElement('div');
            placeholder.className = 'joint-item';
            placeholder.style.color = 'gray';
            placeholder.textContent = 'Waiting for pose detection...';
            container.appendChild(placeholder);
        }
    }
    
    // Add detailed feedback messages
    if (data.feedback && data.feedback.length > 0) {
        const feedbackList = document.createElement('div');
        feedbackList.className = 'feedback-list';
        feedbackList.style.marginTop = '10px';
        feedbackList.style.fontSize = '0.9em';
        feedbackList.dataset.type = 'feedback-list';
        
        data.feedback.forEach(msg => {
            const feedbackMsg = document.createElement('div');
            feedbackMsg.textContent = msg;
            feedbackMsg.style.padding = '3px 0';
            feedbackList.appendChild(feedbackMsg);
        });
        
        container.appendChild(feedbackList);
    }
}

function updateFeedbackValues(data, container) {
    /**
     * Update only the values without rebuilding DOM (prevents flicker)
     */
    // Update angle scores
    data.angle_scores.forEach((angleScore, index) => {
        const item = container.querySelector(`[data-type="angle"][data-index="${index}"]`);
        if (item) {
            const symbol = item.querySelector('.angle-symbol');
            const score = item.querySelector('.joint-score');
            const message = item.querySelector('.joint-message');
            
            if (symbol) {
                symbol.textContent = angleScore.symbol;
                symbol.style.color = angleScore.color;
            }
            if (score) {
                score.textContent = `${angleScore.score.toFixed(1)}%`;
                score.style.color = angleScore.color;
            }
            if (message) {
                message.textContent = `${angleScore.actual_angle}° (target: ${angleScore.target_angle}°, off by ${angleScore.deviation}°)`;
            }
            
            // Update class for status
            item.className = 'joint-item angle-item-' + angleScore.status;
        }
    });
    
    // Update connection scores
    if (data.connection_scores && data.connection_scores.length > 0) {
        data.connection_scores.forEach((conn, index) => {
            const item = container.querySelector(`[data-type="connection"][data-index="${index}"]`);
            if (item) {
                const symbol = item.querySelector('.angle-symbol');
                const score = item.querySelector('.joint-score');
                const message = item.querySelector('.joint-message');
                
                if (symbol) {
                    symbol.textContent = conn.symbol;
                    symbol.style.color = conn.color;
                }
                if (score) {
                    score.textContent = `${conn.score.toFixed(1)}%`;
                    score.style.color = conn.color;
                }
                if (message) {
                    // Use custom message if available (for not detected/low visibility)
                    const messageText = conn.message || 
                        `Distance: ${(conn.distance * 100).toFixed(1)}% (max: ${(conn.max_distance * 100).toFixed(0)}%)`;
                    message.textContent = messageText;
                }
                
                // Update class for status
                item.className = 'joint-item angle-item-' + conn.status;
            }
        });
    }
}

function getAccuracyClass(score) {
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
}

function getScoreClass(score) {
    if (score >= 90) return 'score-excellent';
    if (score >= 75) return 'score-good';
    if (score >= 50) return 'score-fair';
    return 'score-poor';
}

function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    overlay.querySelector('p').textContent = message;
    overlay.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// Notifications removed for cleaner live accuracy experience
// Errors shown via console.log and alerts only for critical issues
