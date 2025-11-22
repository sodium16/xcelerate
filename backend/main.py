from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1 import endpoints
import uvicorn

# Initialize App
app = FastAPI(
    title="EduPulse Hackathon API",
    description="Backend for Student Risk Prediction & AI Agent",
    version="1.0.0"
)

# --- CORS CONFIGURATION ---
# Critical: Allows your React/Next.js frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER REGISTRATION ---
app.include_router(endpoints.router, prefix="/api/v1")

# --- HEALTH CHECK ---
@app.get("/")
def root():
    return {
        "message": "EduPulse API is Online 🚀",
        "docs_url": "http://localhost:8000/docs"
    }

# --- RUNNER ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)