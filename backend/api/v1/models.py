from pydantic import BaseModel
from typing import List, Optional

# --- STUDENT DATA MODELS ---

class StudentRiskProfile(BaseModel):
    student_id: str
    name: str
    risk_score: int          # 0-100
    risk_label: str          # "High Risk", "Moderate", "Safe"
    cgpa: float
    attendance: float
    financial_flag: bool     # True if they need scholarship help
    study_hours: float
    top_risk_factor: str     # e.g., "Low Attendance", "Academic Performance"

class PredictionResponse(BaseModel):
    status: str
    total_students: int
    at_risk_count: int
    data: List[StudentRiskProfile]

# --- AGENT CALL MODELS ---

class CallRequest(BaseModel):
    student_id: str

class CallResponse(BaseModel):
    status: str
    call_id: str
    message: str

class CallSummaryRequest(BaseModel):
    student_id: str
    transcript: str
    sentiment: str  # "Positive", "Neutral", "Stressed"
    action_item: str # "Schedule Meeting", "Scholarship", "None"