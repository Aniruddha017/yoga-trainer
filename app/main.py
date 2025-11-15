from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.config import settings
from app.models.schemas import HealthCheckResponse
from app.api.routes import pose_detection, accuracy, reference, manual_accuracy


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Yoga Pose Accuracy Measurement API - Compare user poses with reference yoga poses",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pose_detection.router, prefix=settings.api_v1_prefix)
app.include_router(accuracy.router, prefix=settings.api_v1_prefix)
app.include_router(reference.router, prefix=settings.api_v1_prefix)
app.include_router(manual_accuracy.router, prefix=settings.api_v1_prefix)

# Mount frontend static files
frontend_dir = settings.base_dir / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend HTML"""
    frontend_file = frontend_dir / "index.html"
    
    if frontend_file.exists():
        with open(frontend_file, 'r') as f:
            return f.read()
    
    return """
    <html>
        <head>
            <title>Yoga Pose Accuracy API</title>
        </head>
        <body>
            <h1>Yoga Pose Accuracy Measurement API</h1>
            <p>Welcome to the Yoga Pose Accuracy API!</p>
            <p>API Documentation: <a href="/docs">/docs</a></p>
            <p>Alternative Docs: <a href="/redoc">/redoc</a></p>
        </body>
    </html>
    """


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Global health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version
    )


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create necessary directories
    settings.reference_poses_dir.mkdir(parents=True, exist_ok=True)
    settings.reference_images_dir.mkdir(parents=True, exist_ok=True)
    settings.reference_keypoints_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"API available at: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
