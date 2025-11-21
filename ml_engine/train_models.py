import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Configuration
DATASET_DIR = "dataset"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Define Domain Configs (Features to use for each)
# We exclude 'dropout_status' (Target) and 'student_id' (ID)
DOMAIN_CONFIG = {
    'engineering': {
        'file': 'engineering.csv',
        'save_name': 'model_eng.pkl'
    },
    'medical': {
        'file': 'medical.csv',
        'save_name': 'model_med.pkl'
    },
    'commerce': {
        'file': 'commerce.csv',
        'save_name': 'model_ca.pkl'
    },
    'mba': {
        'file': 'mba.csv',
        'save_name': 'model_mba.pkl'
    },
    'school': {
        'file': 'school.csv',
        'save_name': 'model_school.pkl'
    }
}

def train_and_save_model(domain_name, config):
    print(f"\n--- Training Domain: {domain_name.upper()} ---")
    
    # 1. Load Data
    file_path = os.path.join(DATASET_DIR, config['file'])
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run generate_data.py first.")
        return

    df = pd.read_csv(file_path)
    
    # 2. Separate X (Features) and y (Target)
    target = 'dropout_status'
    X = df.drop(columns=[target, 'student_id']) # ID is not a feature
    y = df[target]

    # 3. Identify Column Types for Preprocessing
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object']).columns.tolist()

    print(f"Numeric Feats: {len(numeric_features)} | Categorical Feats: {len(categorical_features)}")

    # 4. Build the Pipeline
    # This automates the "Data Cleaning" step during inference too!
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # Full Pipeline: Preprocessing -> Classifier
    clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    # 5. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. Train
    clf.fit(X_train, y_train)

    # 7. Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Training Accuracy: {acc:.4f}")
    # print(classification_report(y_test, y_pred)) # Uncomment for full details

    # 8. Save Model
    save_path = os.path.join(MODEL_DIR, config['save_name'])
    joblib.dump(clf, save_path)
    print(f"Model saved to: {save_path}")

if __name__ == "__main__":
    for domain, config in DOMAIN_CONFIG.items():
        train_and_save_model(domain, config)
    print("\nAll models trained and saved successfully!")