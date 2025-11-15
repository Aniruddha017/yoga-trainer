// Camera management for webcam access

class CameraManager {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.stream = null;
        this.isRunning = false;
        
        // Create a hidden canvas for frame capture (don't interfere with pose overlay)
        this.captureCanvas = document.createElement('canvas');
        this.captureCanvas.style.display = 'none';
        document.body.appendChild(this.captureCanvas);
    }

    async start() {
        /**
         * Start webcam stream
         */
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            });

            this.video.srcObject = this.stream;
            this.isRunning = true;

            // Wait for video to be ready
            await new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });

            // Set canvas dimensions to match video
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Also set capture canvas dimensions
            this.captureCanvas.width = this.video.videoWidth;
            this.captureCanvas.height = this.video.videoHeight;

            return true;
        } catch (error) {
            console.error('Error starting camera:', error);
            throw new Error('Failed to access camera. Please ensure camera permissions are granted.');
        }
    }

    stop() {
        /**
         * Stop webcam stream
         */
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.video) {
            this.video.srcObject = null;
        }
        
        this.isRunning = false;
    }

    captureFrame() {
        /**
         * Capture current video frame as base64 image
         * Uses a hidden canvas to avoid interfering with pose overlay
         * @returns {string} Base64 encoded image
         */
        if (!this.isRunning) {
            throw new Error('Camera is not running');
        }

        const context = this.captureCanvas.getContext('2d');
        
        // Draw current video frame to HIDDEN capture canvas (not the pose overlay canvas)
        context.drawImage(this.video, 0, 0, this.captureCanvas.width, this.captureCanvas.height);
        
        // Convert to base64
        return this.captureCanvas.toDataURL('image/jpeg', 0.8);
    }

    drawVideoToCanvas() {
        /**
         * Draws the current video frame onto the visible pose canvas.
         * This function should be called before drawing keypoints to provide the background.
         * This eliminates flicker and overwrites any external 33-point drawings.
         */
        if (!this.isRunning || !this.video.videoWidth) {
            return;
        }

        const context = this.canvas.getContext('2d');
        
        // Always clear the visible canvas first
        context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw the video frame onto the visible canvas (this eliminates flicker)
        context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
    }

    getVideoElement() {
        return this.video;
    }

    getCanvasElement() {
        return this.canvas;
    }

    isActive() {
        return this.isRunning;
    }
}
