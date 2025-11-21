import sys
import os

# Add the project root to path so we can import from ml_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.predictor import predict_student_risk  # Import the function directly