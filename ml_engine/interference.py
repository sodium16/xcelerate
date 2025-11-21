import joblib
import pandas as pd
import os
import numpy as np

# Load models only once when server starts to save time (Caching)
MODEL_DIR = "models"
MODELS = {}

def load_models():
    """Load all available models into memory."""
    model_files = {
        'engineering': 'model_eng.pkl',
        'medical': 'model_med.pkl',
        'commerce': 'model_ca.pkl',
        'mba': 'model_mba.pkl',
        'school': 'model_school.pkl'
    }
    
    for domain, fname in model_files.items():
        path = os.path.join(MODEL_DIR, fname)
        if os.path.exists(path):
            MODELS[domain] = joblib.load(path)
            print(f"Loaded {domain} model.")
        else:
            print(f"Warning: {fname} not found.")

# Initialize models immediately
load_models()

def predict_dropout_risk(student_data: dict, domain: str):
    """
    Input: 
        student_data (dict): The raw JSON from frontend. 
                             e.g., {'attendance_rate': 60, 'gender': 'Male', ...}
        domain (str): 'engineering', 'medical', etc.
    
    Output:
        probability (float): 0 to 100 (Risk Percentage)
    """
    domain = domain.lower()
    
    if domain not in MODELS:
        return {"error": "Invalid Domain or Model not loaded"}
    
    model = MODELS[domain]
    
    # Convert dict to DataFrame (Expected by Pipeline)
    input_df = pd.DataFrame([student_data])
    
    try:
        # The pipeline handles all encoding/scaling automatically!
        # predict_proba returns [[prob_0, prob_1]]
        probability_class_1 = model.predict_proba(input_df)[0][1]
        
        risk_percentage = round(probability_class_1 * 100, 2)
        return risk_percentage
        
    except Exception as e:
        return {"error": str(e)}

# --- TEST RUN ---
if __name__ == "__main__":
    # Mock data coming from Frontend
    test_input = {
        'gender': 'Male',
        'age': 21,
        'attendance_rate': 45.5, # Low attendance -> Should be High Risk
        'study_hours_per_day': 2,
        'past_failures': 1,
        'tuition_fee_status': 'Unpaid',
        'internet_access': 'Yes',
        # Engineering Specifics
        'department': 'CS',
        'cgpa': 4.2,             # Low CGPA -> Should be High Risk
        'lab_performance': 50,
        'backlog_history': 1,
        'programming_skills_score': 3
    }
    
    print("Testing Prediction for Engineering Student...")
    score = predict_dropout_risk(test_input, 'engineering')
    print(f"Dropout Risk: {score}%")