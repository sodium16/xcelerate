# Path: backend/db/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Create the SQLite Database URL
# This will create a file named 'sql_app.db' in your backend folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Create the Engine
# check_same_thread=False is needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create the SessionLocal class
# We use this to create a database session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Base class
# All our database models will inherit from this
Base = declarative_base()

# --- DB MODELS (Tables) ---

class StudentDB(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True)
    name = Column(String)
    risk_score = Column(Integer)
    risk_label = Column(String)
    cgpa = Column(Float)
    attendance = Column(Float)
    financial_flag = Column(Boolean, default=False)
    study_hours = Column(Float)
    top_risk_factor = Column(String)

class CallLogDB(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    transcript = Column(String)
    sentiment = Column(String)
    action_item = Column(String)
    timestamp = Column(String) # In real app, use DateTime

# 5. Dependency Injection
# This function is used in endpoints.py to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 6. Auto-create Tables
# This runs when this file is imported to ensure tables exist
Base.metadata.create_all(bind=engine)