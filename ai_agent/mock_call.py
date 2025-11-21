# Path: ai_agent/mock_call.py
import requests
import time
import random

# Configuration
API_URL = "http://localhost:8000/api/v1"

def simulate_agent_workflow(student_id):
    print(f"🤖 [Agent System] Received trigger for Student {student_id}...")
    print("📞 Dialing... (Simulating Vapi.ai / Twilio connection)")
    
    # Simulate call duration
    time.sleep(2) 
    print("🗣️  Conversation in progress...")
    time.sleep(2)
    
    # Generate a random outcome
    outcomes = [
        {"sentiment": "Stressed", "action": "Schedule Counselor", "text": "Student is overwhelmed with part-time job. Requesting extension on assignments."},
        {"sentiment": "Neutral", "action": "None", "text": "Student was sick last week. Will submit medical certificate tomorrow."},
        {"sentiment": "Positive", "action": "Scholarship Info", "text": "Student is focused but worried about fees. Asked for scholarship details."}
    ]
    result = random.choice(outcomes)
    
    print("✅ Call Finished. Sending Summary to Backend Webhook...")
    
    # PAYLOAD (Matches your Backend Model)
    payload = {
        "student_id": student_id,
        "transcript": result["text"],
        "sentiment": result["sentiment"],
        "action_item": result["action"]
    }
    
    try:
        response = requests.post(f"{API_URL}/agent/webhook/summary", json=payload)
        if response.status_code == 200:
            print("🚀 Success! Backend accepted the call log.")
            print(f"   Server Response: {response.json()}")
        else:
            print(f"❌ Backend Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    # Test with a fake ID
    test_id = input("Enter Student ID to simulate call (e.g. 101): ")
    simulate_agent_workflow(test_id)