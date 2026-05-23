"""
FastAPI Backend — Urban Growth Detection System
------------------------------------------------
Endpoints:
  GET  /            → Health check
  POST /detect      → Main change detection endpoint
  GET  /describe    → AI description using Gemini (bonus)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from models.change_detector import UrbanChangeDetector
from utils.image_utils import validate_image, run_parallel

load_dotenv()

app = FastAPI(
    title="Urban Growth Detection API",
    description="Detects urban changes from multi-temporal satellite images",
    version="1.0.0",
)

# Allow React frontend (running on port 5173) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detector once at startup
detector = UrbanChangeDetector()


@app.get("/")
def health_check():
    """Simple health check — confirms server is running"""
    return {"status": "ok", "message": "Urban Growth Detection API is running"}


@app.post("/detect")
async def detect_changes(
    before: UploadFile = File(..., description="Satellite image - earlier date"),
    after: UploadFile = File(..., description="Satellite image - later date"),
    use_ray: bool = False,
):
    """
    Main endpoint: Upload two satellite images, get change analysis back.
    
    - before: Image from earlier time period (e.g., 2015)
    - after:  Image from later time period (e.g., 2024)  
    - use_ray: Set True to use Ray distributed processing
    """
    # Read uploaded file bytes
    before_bytes = await before.read()
    after_bytes = await after.read()

    # Validate both images
    if not validate_image(before_bytes):
        raise HTTPException(status_code=400, detail="Invalid 'before' image file")
    if not validate_image(after_bytes):
        raise HTTPException(status_code=400, detail="Invalid 'after' image file")

    try:
        if use_ray:
            result = run_parallel(before_bytes, after_bytes)
        else:
            # Direct processing
            result = detector.detect(before_bytes, after_bytes)

        return JSONResponse(content={"success": True, "data": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/describe")
async def describe_changes(statistics: dict):
    """
    Uses Google Gemini AI to generate a human-readable description
    of the detected changes — integrating Gen AI concepts from Module 4.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        return {
            "description": (
                f"Analysis complete. Detected {statistics.get('change_percentage', 0)}% "
                f"urban change classified as '{statistics.get('growth_classification', 'Unknown')}'. "
                f"Found {statistics.get('num_change_clusters', 0)} distinct change zones "
                f"with {statistics.get('severity', 'Unknown')} severity."
            )
        }

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an urban planning expert analyzing satellite change detection results.
        Write a brief, clear 3-sentence analysis for a non-technical audience.
        
        Results:
        - Change detected: {statistics.get('change_percentage')}% of the area
        - Classification: {statistics.get('growth_classification')}
        - Severity: {statistics.get('severity')}
        - Number of change clusters: {statistics.get('num_change_clusters')}
        - Average change intensity: {statistics.get('avg_change_intensity')}%
        
        Describe what this means for urban development in simple terms.
        """

        response = model.generate_content(prompt)
        return {"description": response.text}

    except Exception as e:
        return {"description": f"AI description unavailable: {str(e)}"}