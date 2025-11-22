import pandas as pd
import numpy as np
from faker import Faker
import random
import os

# Initialize Faker
fake = Faker('en_IN')
OUTPUT_DIR = "backend/sample_batch_uploads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_balanced_profile(risk_type):
    """
    Generates a single student profile engineered to match a specific risk type.
    """
    profile = {
        'student_id': f"STU_{random.randint(100000, 999999)}",
        'name': fake.name(),
        'family_income': random.choice(['High', 'Medium', 'Low']),
        'scholarship': random.choice(['Yes', 'No']),
    }

    if risk_type == 'high':
        # Traits of a High Risk Student
        profile['attendance_rate'] = random.uniform(40, 65) # Low
        profile['cgpa'] = random.uniform(3.0, 5.5)          # Low
        profile['study_hours_per_day'] = random.randint(0, 2)
        profile['past_failures'] = random.randint(2, 4)
        
        # Domain specifics (Low scores)
        profile['project_score'] = random.randint(20, 50)
        profile['coding_skills'] = random.randint(1, 3)
        profile['clinical_score'] = random.randint(40, 60)
        profile['hospital_hours'] = random.randint(0, 5)
        profile['audit_hours'] = random.randint(0, 50)
        profile['law_score'] = random.randint(20, 45)
        profile['internship_score'] = random.randint(1, 3)
        profile['case_studies'] = random.randint(0, 5)
        profile['homework_rate'] = random.randint(20, 50)
        profile['parent_meetings'] = random.randint(0, 1)

    elif risk_type == 'moderate':
        # Traits of a Moderate Risk Student
        profile['attendance_rate'] = random.uniform(66, 84) # Average
        profile['cgpa'] = random.uniform(5.6, 7.5)          # Average
        profile['study_hours_per_day'] = random.randint(3, 5)
        profile['past_failures'] = random.choice([0, 1])
        
        # Domain specifics (Average scores)
        profile['project_score'] = random.randint(51, 75)
        profile['coding_skills'] = random.randint(4, 6)
        profile['clinical_score'] = random.randint(61, 79)
        profile['hospital_hours'] = random.randint(10, 20)
        profile['audit_hours'] = random.randint(100, 250)
        profile['law_score'] = random.randint(50, 70)
        profile['internship_score'] = random.randint(4, 7)
        profile['case_studies'] = random.randint(10, 25)
        profile['homework_rate'] = random.randint(55, 80)
        profile['parent_meetings'] = random.randint(2, 3)

    else: # 'safe'
        # Traits of a Safe Student
        profile['attendance_rate'] = random.uniform(85, 100) # High
        profile['cgpa'] = random.uniform(7.6, 10.0)          # High
        profile['study_hours_per_day'] = random.randint(6, 10)
        profile['past_failures'] = 0
        
        # Domain specifics (High scores)
        profile['project_score'] = random.randint(80, 100)
        profile['coding_skills'] = random.randint(7, 10)
        profile['clinical_score'] = random.randint(85, 100)
        profile['hospital_hours'] = random.randint(25, 40)
        profile['audit_hours'] = random.randint(300, 500)
        profile['law_score'] = random.randint(75, 100)
        profile['internship_score'] = random.randint(8, 10)
        profile['case_studies'] = random.randint(30, 50)
        profile['homework_rate'] = random.randint(85, 100)
        profile['parent_meetings'] = random.randint(4, 5)

    # Round floats
    profile['attendance_rate'] = round(profile['attendance_rate'], 1)
    profile['cgpa'] = round(profile['cgpa'], 2)
    
    return profile

def generate_balanced_dataset(n=50):
    """Generates n students, split evenly among risk categories."""
    data = []
    # Force distribution: 1/3 High, 1/3 Moderate, 1/3 Safe
    targets = ['high'] * (n // 3) + ['moderate'] * (n // 3) + ['safe'] * (n - 2*(n // 3))
    random.shuffle(targets)
    
    for risk_type in targets:
        data.append(generate_balanced_profile(risk_type))
        
    return pd.DataFrame(data)

def generate_csvs():
    base_df = generate_balanced_dataset(50)
    
    # 1. Engineering
    cols = ['student_id', 'name', 'attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'family_income', 'scholarship', 'project_score', 'coding_skills']
    base_df[cols].to_csv(f"{OUTPUT_DIR}/batch_engineering.csv", index=False)

    # 2. Medical
    cols = ['student_id', 'name', 'attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'family_income', 'scholarship', 'clinical_score', 'hospital_hours']
    base_df[cols].to_csv(f"{OUTPUT_DIR}/batch_medical.csv", index=False)

    # 3. CA
    cols = ['student_id', 'name', 'attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'family_income', 'scholarship', 'audit_hours', 'law_score']
    base_df[cols].to_csv(f"{OUTPUT_DIR}/batch_ca.csv", index=False)

    # 4. MBA
    cols = ['student_id', 'name', 'attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'family_income', 'scholarship', 'internship_score', 'case_studies']
    base_df[cols].to_csv(f"{OUTPUT_DIR}/batch_mba.csv", index=False)

    # 5. School
    cols = ['student_id', 'name', 'attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'family_income', 'scholarship', 'homework_rate', 'parent_meetings']
    base_df[cols].to_csv(f"{OUTPUT_DIR}/batch_school.csv", index=False)

    print(f"✅ Generated 5 BALANCED batch CSVs in '{OUTPUT_DIR}/'")

if __name__ == "__main__":
    generate_csvs()