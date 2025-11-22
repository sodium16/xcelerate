import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Paths
DATA_DIR = "dataset"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# --- THE ARENA: Define Models & Hyperparameters to Test ---
MODEL_ZOO = {
    "RandomForest": {
        "model": RandomForestClassifier(random_state=42),
        "params": {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 20, None],  # "Different branches/depth"
            'min_samples_split': [2, 5]
        }
    },
    "GradientBoosting": {
        "model": GradientBoostingClassifier(random_state=42),
        "params": {
            'n_estimators': [50, 100],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7]
        }
    },
    "LogisticRegression": {
        "model": LogisticRegression(max_iter=1000, random_state=42),
        "params": {
            'C': [0.1, 1, 10]
        }
    }
}

def train_and_optimize(domain_file, model_name, features):
    print(f"\n{'='*70}")
    print(f"🔬 Optimizing Model for: {model_name.upper()}")
    print(f"{'='*70}")
    
    try:
        # 1. Load Data
        file_path = f"{DATA_DIR}/{domain_file}"
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        
        # Validate Features
        available_features = [f for f in features if f in df.columns]
        if len(available_features) != len(features):
            print(f"   ⚠️ Missing features! Found: {len(available_features)}/{len(features)}")
            return

        X = df[available_features]
        y = df['dropout_status']
        
        # 2. Split Data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        best_score = 0
        best_model = None
        best_algo_name = ""

        # 3. The Battle: Loop through algorithms
        for algo_name, config in MODEL_ZOO.items():
            print(f"   👉 Testing {algo_name}...", end=" ")
            
            # Grid Search for Hyperparameter Tuning
            clf = GridSearchCV(config["model"], config["params"], cv=3, scoring='accuracy', n_jobs=-1)
            clf.fit(X_train, y_train)
            
            # Evaluate on Test Set
            y_pred = clf.best_estimator_.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            
            print(f"Score: {score:.2%}")
            
            # Check if this is the new champion
            if score > best_score:
                best_score = score
                best_model = clf.best_estimator_
                best_algo_name = algo_name

        # 4. Announce Winner
        print(f"\n🏆 WINNER: {best_algo_name} with {best_score:.2%} Accuracy")
        print(f"   ⚙️ Best Params: {best_model.get_params()}")
        
        # 5. Final Report
        y_final_pred = best_model.predict(X_test)
        print("\n   --- Final Classification Report ---")
        print(classification_report(y_test, y_final_pred, target_names=['Safe', 'Risk']))
        
        # 6. Save the Champion
        save_path = f"{MODEL_DIR}/{model_name}.pkl"
        joblib.dump(best_model, save_path)
        print(f"💾 Saved best model to: {save_path}")
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    # 1. Engineering
    train_and_optimize("engineering.csv", "model_engineering", 
          ['attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'project_score', 'coding_skills'])

    # 2. Medical
    train_and_optimize("medical.csv", "model_med", 
          ['attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'clinical_score', 'hospital_hours'])

    # 3. CA
    train_and_optimize("ca.csv", "model_ca", 
          ['attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'audit_hours', 'law_score'])

    # 4. MBA
    train_and_optimize("mba.csv", "model_mba", 
          ['attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'internship_score', 'case_studies'])

    # 5. School
    train_and_optimize("school.csv", "model_school", 
          ['attendance_rate', 'cgpa', 'study_hours_per_day', 'past_failures', 'homework_rate', 'parent_meetings'])