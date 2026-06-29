import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override standard python command to use active venv python interpreter
import mcp_client
mcp_client.SERVER_PARAMS.command = sys.executable

from main import app

client = TestClient(app)

def test_divya_flow():
    candidate_id = "90216606-920f-4f8c-9222-541ac0d4271c"
    print(f"--- Running API Workflow for Candidate UUID: {candidate_id} ---")
    
    # 1. POST /analyze
    res = client.post("/analyze", json={"candidate_id": candidate_id})
    print(f"\n[Step 1] POST /analyze status: {res.status_code}")
    print(f"Response: {res.json()}")
    
    data = res.json()
    if data.get("status") == "awaiting_approval":
        session_id = data["session_id"]
        
        # 2. GET /hitl/pending/{session_id}
        res_pending = client.get(f"/hitl/pending/{session_id}")
        print(f"\n[Step 2] GET /hitl/pending status: {res_pending.status_code}")
        print(f"Response: {res_pending.json()}")
        
        # 3. POST /hitl/respond
        res_respond = client.post("/hitl/respond", json={"session_id": session_id, "decision": "approved"})
        print(f"\n[Step 3] POST /hitl/respond status: {res_respond.status_code}")
        print(f"Response: {res_respond.json()}")
        
        # 4. GET /nba/queue
        res_queue = client.get("/nba/queue")
        print(f"\n[Step 4] GET /nba/queue status: {res_queue.status_code}")
        print(f"Response: {res_queue.json()}")

if __name__ == "__main__":
    test_divya_flow()
