import pandas as pd
import numpy as np
from faker import Faker
import random
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)

# Configuration
NUM_ROWS = 30000
OUTPUT_DIR = "dataset"

# Create directory if it doesn't exist (based on your image structure)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_base_data(n=NUM_ROWS):
    """
    Generates the core columns common to ALL students.
    """
    data = {
        'student_id': [f"STU_{random.randint(100000, 999999)}" for _ in range(n)],
        'gender': np.random.choice(['Male', 'Female'], n),
        'age': np.random.randint(17, 25, n),
        'attendance_rate': np.random.normal(75, 15, n).clip(0, 100),  # Normal dist around 75%
        'study_hours_per_day': np.random.randint(1, 10, n),
        'past_failures': np.random.choice([0, 1, 2, 3], n, p=[0.7, 0.2, 0.08, 0.02]),
        'tuition_fee_status': np.random.choice(['Paid', 'Unpaid', 'Scholarship'], n, p=[0.6, 0.3, 0.1]),
        'internet_access': np.random.choice(['Yes', 'No'], n, p=[0.85, 0.15]),
    }
    return pd.DataFrame(data)

def add_target_variable(df):
    """
    Logic to determine dropout risk based on data.
    Rule: Low attendance + Low Grades/Performance + Some Noise = Dropout
    """
    # Normalize score to 0-100 for calculation regardless of domain
    if 'cgpa' in df.columns:
        score_metric = df['cgpa'] * 10
    elif 'internal_assessment_score' in df.columns:
        score_metric = df['internal_assessment_score']
    elif 'grade_avg' in df.columns:
        score_metric = df['grade_avg']
    else:
        score_metric = 50 # Fallback

    # Base Probability
    # If attendance < 60 OR score < 40, high risk
    risk_score = np.where(df['attendance_rate'] < 65, 1, 0) + \
                 np.where(score_metric < 45, 1, 0) + \
                 np.where(df['past_failures'] > 0, 0.5, 0)
    
    # Add noise (randomness) so the model doesn't just memorize the rules
    noise = np.random.normal(0, 0.2, len(df))
    final_risk = risk_score + noise
    
    # Threshold for dropout (1 = Dropout, 0 = Stay)
    df['dropout_status'] = np.where(final_risk > 0.8, 1, 0)
    return df

# ==========================================
# 1. ENGINEERING DATASET
# ==========================================
def generate_engineering():
    print("Generating Engineering Data...")
    df = generate_base_data()
    
    # Domain Specifics
    df['department'] = np.random.choice(['CS', 'IS', 'EC', 'ME', 'CV'], NUM_ROWS)
    df['cgpa'] = np.random.normal(6.5, 1.5, NUM_ROWS).clip(0, 10).round(2)
    df['lab_performance'] = np.random.randint(40, 100, NUM_ROWS) # Marks out of 100
    df['backlog_history'] = np.random.choice([0, 1, 2, 3], NUM_ROWS, p=[0.6, 0.2, 0.15, 0.05])
    df['programming_skills_score'] = np.random.randint(1, 10, NUM_ROWS) # Self rating
    
    df = add_target_variable(df)
    df.to_csv(f"{OUTPUT_DIR}/engineering.csv", index=False)
    print(f"Saved {OUTPUT_DIR}/engineering.csv")

# ==========================================
# 2. MEDICAL DATASET
# ==========================================
def generate_medical():
    print("Generating Medical Data...")
    df = generate_base_data()
    
    # Domain Specifics
    df['specialization'] = np.random.choice(['General', 'Dental', 'Ayurveda', 'Nursing'], NUM_ROWS)
    df['internal_assessment_score'] = np.random.normal(60, 15, NUM_ROWS).clip(0, 100).round(1)
    df['clinical_rotation_score'] = np.random.randint(50, 100, NUM_ROWS)
    df['neet_pg_mock_score'] = np.random.randint(200, 800, NUM_ROWS)
    df['night_shift_hours'] = np.random.randint(0, 40, NUM_ROWS)
    
    df = add_target_variable(df)
    df.to_csv(f"{OUTPUT_DIR}/medical.csv", index=False)
    print(f"Saved {OUTPUT_DIR}/medical.csv")

# ==========================================
# 3. COMMERCE / CA DATASET
# ==========================================
def generate_commerce():
    print("Generating Commerce/CA Data...")
    df = generate_base_data()
    
    # Domain Specifics
    df['course_stream'] = np.random.choice(['B.Com', 'CA', 'BBA', 'Finance'], NUM_ROWS)
    df['grade_avg'] = np.random.normal(65, 12, NUM_ROWS).clip(0, 100).round(1)
    df['articleship_completed'] = np.random.choice(['Yes', 'No'], NUM_ROWS)
    df['audit_hours_logged'] = np.where(df['articleship_completed'] == 'Yes', 
                                        np.random.randint(100, 500, NUM_ROWS), 0)
    df['ipcc_group_cleared'] = np.random.choice(['Both', 'Group 1', 'None'], NUM_ROWS)
    
    df = add_target_variable(df)
    df.to_csv(f"{OUTPUT_DIR}/commerce.csv", index=False)
    print(f"Saved {OUTPUT_DIR}/commerce.csv")

# ==========================================
# 4. MBA DATASET
# ==========================================
def generate_mba():
    print("Generating MBA Data...")
    df = generate_base_data()
    
    # Domain Specifics
    df['specialization'] = np.random.choice(['HR', 'Marketing', 'Finance', 'Ops'], NUM_ROWS)
    df['cgpa'] = np.random.normal(7.0, 1.2, NUM_ROWS).clip(0, 10).round(2)
    df['case_study_score'] = np.random.randint(10, 50, NUM_ROWS) # Out of 50
    df['internship_experience_months'] = np.random.randint(0, 24, NUM_ROWS)
    df['employability_test_score'] = np.random.randint(400, 800, NUM_ROWS)
    
    df = add_target_variable(df)
    df.to_csv(f"{OUTPUT_DIR}/mba.csv", index=False)
    print(f"Saved {OUTPUT_DIR}/mba.csv")

# ==========================================
# 5. SCHOOL DATASET
# ==========================================
def generate_school():
    print("Generating School Data...")
    df = generate_base_data()
    
    # Domain Specifics
    df['class_level'] = np.random.choice(['8th', '9th', '10th', '11th', '12th'], NUM_ROWS)
    df['grade_avg'] = np.random.normal(70, 15, NUM_ROWS).clip(0, 100).round(1)
    df['parent_meeting_attendance'] = np.random.choice(['Regular', 'Irregular', 'Never'], NUM_ROWS)
    df['homework_completion_rate'] = np.random.randint(0, 100, NUM_ROWS)
    df['extra_curricular_participation'] = np.random.choice(['Yes', 'No'], NUM_ROWS)
    
    df = add_target_variable(df)
    df.to_csv(f"{OUTPUT_DIR}/school.csv", index=False)
    print(f"Saved {OUTPUT_DIR}/school.csv")

if __name__ == "__main__":
    print("Starting EduPulse Data Generation...")
    generate_engineering()
    generate_medical()
    generate_commerce()
    generate_mba()
    generate_school()
    print("All datasets generated successfully in 'backend/dataset/'")