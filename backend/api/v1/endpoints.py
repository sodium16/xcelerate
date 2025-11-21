from fastapi import APIRouter, UploadFile, File, HTTPException
from .models import PredictionResponse, StudentRiskProfile, CallResponse, CallSummaryRequest
import pandas as pd
import io
import random
import os
import joblib

router = APIRouter()

# --- MODEL LOADING LOGIC ---
# Global cache to store models so we don't reload them on every request
MODELS = {
    "engineering": None,
    "medical": None,
    "commerce": None
}

def load_model(domain: str):
    """
    Attempts to load a trained .pkl model. 
    If not found, returns None (triggering Mock Mode).
    """
    # Adjust path to where Member 1 saves the models
    model_path = os.path.join(os.path.dirname(__file__), f"../../../ml_engine/models/model_{domain}.pkl")
    
    if MODELS.get(domain) is None:
        if os.path.exists(model_path):
            try:
                MODELS[domain] = joblib.load(model_path)
                print(f"✅ Loaded Real Model: {model_path}")
            except Exception as e:
                print(f"⚠️ Error loading model {model_path}: {e}")
                return None
        else:
            print(f"⚠️ Model not found at {model_path}. Using Mock Logic.")
            return None
    return MODELS[domain]


# --- ROUTE 1: UPLOAD & PREDICT ---
@router.post("/predict/{domain_type}", response_model=PredictionResponse)
async def predict_students(domain_type: str, file: UploadFile = File(...)):
    
    # 1. Read the CSV file
    try:
        contents = await file.read()
        # Decode bytes to string
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

    # 2. Load the Model (or fail gracefully to Mock Mode)
    model = load_model(domain_type)
    
    processed_data = []
    at_risk_counter = 0

    # 3. Process each student
    for index, row in df.iterrows():
        # Extract IDs safely
        student_id = str(row.get('student_id', f"TEMP_{index}"))
        name = row.get('name', f"Student {student_id}")
        
        # Extract Features
        # NOTE: Ensure these column names match your CSV exactly
        attendance = float(row.get('attendance_rate', 0))
        cgpa = float(row.get('cgpa', 0))
        study_hours = float(row.get('study_hours_per_day', 0))
        failures = int(row.get('past_failures', 0))
        
        # --- PREDICTION ENGINE ---
        if model:
            # REAL ML PREDICTION
            # Features must match training order: [attendance, cgpa, study_hours, failures]
            features = [[attendance, cgpa, study_hours, failures]]
            try:
                # Assuming class 1 is "At Risk"
                risk_probability = model.predict_proba(features)[0][1]
                risk_score = int(risk_probability * 100)
            except:
                # Fallback if model fails on specific row
                risk_score = 50
        else:
            # MOCK LOGIC (For Hackathon Demos/Testing)
            # High Risk if: Low Attendance OR Low CGPA OR High Failures
            if attendance < 70 or cgpa < 5.0 or failures > 1:
                base_risk = random.randint(75, 98)
            elif attendance < 85:
                base_risk = random.randint(40, 70)
            else:
                base_risk = random.randint(5, 30)
            risk_score = base_risk

        # --- LOGIC LAYER ---
        # Determine Label
        if risk_score >= 80:
            label = "High Risk"
            at_risk_counter += 1
        elif risk_score >= 50:
            label = "Moderate"
        else:
            label = "Safe"

        # Determine Reason
        reason = "General Performance"
        if attendance < 75:
            reason = "Critical Attendance"
        elif cgpa < 5.0:
            reason = "Academic Decline"
        elif failures > 0:
            reason = "Past Failures"

        # Financial Logic (Feature: Scholarship Matcher)
        # Checks if income is low (assuming 'family_income' column exists)
        # and if they DON'T have a scholarship yet.
        needs_aid = False
        income_val = str(row.get('family_income', 'High')).lower()
        scholarship_val = str(row.get('scholarship', 'Yes')).lower()
        
        if ('<aw' in income_val or 'low' in income_val) and ('no' in scholarship_val):
            needs_aid = True

        # Build Object
        student_profile = StudentRiskProfile(
            student_id=student_id,
            name=name,
            risk_score=risk_score,
            risk_label=label,
            cgpa=cgpa,
            attendance=attendance,
            financial_flag=needs_aid,
            study_hours=study_hours,
            top_risk_factor=reason
        )
        processed_data.append(student_profile)

    # 4. Return Final JSON
    return PredictionResponse(
        status="success",
        total_students=len(processed_data),
        at_risk_count=at_risk_counter,
        data=processed_data
    )


# --- ROUTE 2: TRIGGER CALL ---
@router.post("/agent/call/{student_id}", response_model=CallResponse)
async def trigger_call(student_id: str):
    """
    Frontend calls this to start the AI voice agent.
    """
    # TODO: Integrate Vapi.ai / Twilio SDK here
    print(f"📞 Dialing Student {student_id}...")
    
    return CallResponse(
        status="queued",
        call_id=f"call_{random.randint(10000, 99999)}",
        message=f"AI Agent initialized for {student_id}"
    )


# --- ROUTE 3: WEBHOOK (Receive Summary) ---
@router.post("/agent/webhook/summary")
async def receive_call_summary(summary: CallSummaryRequest):
    """
    The AI Agent script hits this endpoint when the call finishes.
    """
    print(f"✅ Call Completed for ID: {summary.student_id}")
    print(f"📝 Transcript: {summary.transcript}")
    print(f"💡 Action Item: {summary.action_item}")
    
    # In a real app, save this to DB here.
    return {"status": "received"}