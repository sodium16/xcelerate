import pandas as pd
import numpy as np
from faker import Faker
import random
import os

fake = Faker('en_IN')
NUM_ROWS = 30000
OUTPUT_DIR = "dataset" 
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_base_data(n=NUM_ROWS):
    print(f"   -> Simulating {n} student lives...")
    
    # --- REALISTIC DISTRIBUTIONS ---
    
    # Attendance: Beta Dist (Skewed High). Most attend 75-90%, but there's a tail of bunks.
    # a=10, b=2 gives a peak around 0.83 (83%)
    attendance = np.random.beta(10, 2, n) * 100
    attendance = attendance.clip(20, 100).round(1)
    
    # Study Hours: Gamma Dist. Most people study 2-4 hours. The "grinders" do 10+.
    study_hours = np.random.gamma(shape=3.0, scale=1.5, size=n).clip(0, 14).round(1)
    
    # Past Failures: Poisson. Most have 0. Some have 1. Very few have 3+.
    failures = np.random.poisson(lam=0.3, size=n).clip(0, 5)
    
    data = {
        'student_id': [f"STU_{random.randint(100000, 999999)}" for _ in range(n)],
        'name': [fake.name() for _ in range(n)],
        'email': [fake.email() for _ in range(n)],
        'phone_number': [f"+91{random.randint(6000000000, 9999999999)}" for _ in range(n)],
        'gender': np.random.choice(['Male', 'Female'], n),
        'age': np.random.randint(18, 24, n),
        'attendance_rate': attendance,
        'study_hours_per_day': study_hours,
        'past_failures': failures,
        'family_income': np.random.choice(['High', 'Medium', 'Low'], n, p=[0.3, 0.5, 0.2]), 
        'scholarship': np.random.choice(['Yes', 'No'], n, p=[0.15, 0.85]),
    }
    return pd.DataFrame(data)

def calculate_survival_score(df, score_col):
    """
    Calculates a 'Survival Score' (0 to 1). 
    1.0 = Guaranteed Grad. 0.0 = Guaranteed Dropout.
    """
    # Normalize academic score (CGPA or similar) to 0-1
    norm_score = df[score_col] / df[score_col].max()
    
    # Normalize attendance to 0-1
    norm_att = df['attendance_rate'] / 100.0
    
    # Penalize failures exponentially (1 fail is bad, 3 is deadly)
    penalty_fail = (df['past_failures'] ** 1.5) * 0.15
    
    # Boost for study hours (diminishing returns after 8 hours)
    boost_study = np.log1p(df['study_hours_per_day']) * 0.05
    
    # --- THE REAL WORLD EQUATION ---
    # Academics (40%) + Attendance (30%) + Grit/Study (10%) - Failures (Penalty)
    survival = (norm_score * 0.4) + (norm_att * 0.3) + boost_study - penalty_fail
    
    # Add significant randomness (Life events, stress, health)
    # Normal distribution, std_dev=0.1 (10% variance)
    survival += np.random.normal(0, 0.1, len(df))
    
    return survival

def assign_dropout_status(df, survival_scores):
    """
    Assigns 0 or 1 based on the 'Survival Score', but creates a explicit 'Grey Area'.
    """
    conditions = [
        (survival_scores < 0.35),  # THE DANGER ZONE: High prob of dropout
        (survival_scores > 0.65)   # THE SAFE ZONE: High prob of staying
    ]
    choices = [1, 0] # 1=Dropout, 0=Safe
    
    # Default value for the middle (0.35 to 0.65) is -1 (Placeholder)
    df['dropout_status'] = np.select(conditions, choices, default=-1)
    
    # --- THE BUBBLE LOGIC (Creating Moderate Risks) ---
    # For students in the "Grey Area" (0.35 - 0.65), it's a toss-up.
    # This confuses the AI just enough to make it predict "45%" or "55%" risk.
    
    mask_grey = df['dropout_status'] == -1
    # In the grey zone, survival is random chance (50/50 split)
    df.loc[mask_grey, 'dropout_status'] = np.random.choice([0, 1], size=mask_grey.sum(), p=[0.6, 0.4])
    
    return df

# --- GENERATORS ---

def generate_engineering():
    df = generate_base_data()
    df['department'] = np.random.choice(['CS', 'EC', 'ME'], NUM_ROWS)
    
    # Engineering grades are usually lower on average (tough grading)
    df['cgpa'] = np.random.normal(6.8, 1.2, NUM_ROWS).clip(4, 10).round(2)
    df['project_score'] = np.random.randint(20, 100, NUM_ROWS)
    df['coding_skills'] = np.random.randint(1, 10, NUM_ROWS)
    
    # Calculate survival based on CGPA and Coding
    survival = calculate_survival_score(df, 'cgpa')
    # Bonus survival for good coders (even if grades are bad)
    survival += (df['coding_skills'] / 20.0)
    
    df = assign_dropout_status(df, survival)
    df.to_csv(f"{OUTPUT_DIR}/engineering.csv", index=False)

def generate_medical():
    df = generate_base_data()
    df['specialization'] = np.random.choice(['General', 'Dental'], NUM_ROWS)
    # Med students have higher average grades usually
    df['cgpa'] = np.random.normal(7.5, 1.0, NUM_ROWS).clip(5, 10).round(2)
    df['clinical_score'] = np.random.randint(30, 100, NUM_ROWS)
    df['hospital_hours'] = np.random.randint(0, 50, NUM_ROWS)
    
    survival = calculate_survival_score(df, 'clinical_score') 
    df = assign_dropout_status(df, survival)
    df.to_csv(f"{OUTPUT_DIR}/medical.csv", index=False)

def generate_commerce():
    df = generate_base_data()
    df['course_stream'] = np.random.choice(['B.Com', 'CA'], NUM_ROWS)
    df['cgpa'] = np.random.normal(7.0, 1.4, NUM_ROWS).clip(4, 10).round(2)
    df['audit_hours'] = np.random.randint(0, 500, NUM_ROWS)
    df['law_score'] = np.random.randint(30, 100, NUM_ROWS)
    
    survival = calculate_survival_score(df, 'law_score')
    df = assign_dropout_status(df, survival)
    df.to_csv(f"{OUTPUT_DIR}/ca.csv", index=False)

def generate_mba():
    df = generate_base_data()
    df['specialization'] = np.random.choice(['HR', 'Marketing'], NUM_ROWS)
    df['cgpa'] = np.random.normal(7.2, 1.0, NUM_ROWS).clip(5, 10).round(2)
    df['internship_score'] = np.random.randint(1, 10, NUM_ROWS)
    df['case_studies'] = np.random.randint(5, 50, NUM_ROWS)
    
    survival = calculate_survival_score(df, 'cgpa')
    df = assign_dropout_status(df, survival)
    df.to_csv(f"{OUTPUT_DIR}/mba.csv", index=False)

def generate_school():
    df = generate_base_data()
    df['class_level'] = np.random.choice(['10th', '12th'], NUM_ROWS)
    df['cgpa'] = np.random.normal(7.5, 1.5, NUM_ROWS).clip(4, 10).round(2)
    df['homework_rate'] = np.random.randint(20, 100, NUM_ROWS)
    df['parent_meetings'] = np.random.randint(0, 5, NUM_ROWS)
    
    survival = calculate_survival_score(df, 'homework_rate')
    df = assign_dropout_status(df, survival)
    df.to_csv(f"{OUTPUT_DIR}/school.csv", index=False)

if __name__ == "__main__":
    print("🚀 Generating REAL-WORLD Simulation Data...")
    generate_engineering()
    generate_medical()
    generate_commerce()
    generate_mba()
    generate_school()
    print("✅ Done.")
