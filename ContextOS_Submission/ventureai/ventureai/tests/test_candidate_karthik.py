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

def test_karthik_flow():
    candidate_id = "0faf4a3d-6cf9-4b53-8415-e6a29b0cb11a"
    print(f"--- Running API Workflow for Candidate UUID: {candidate_id} ---")
    
    # 1. POST /analyze
    res = client.post("/analyze", json={"candidate_id": candidate_id})
    print(f"POST /analyze status: {res.status_code}")
    print(f"Response: {res.json()}")

if __name__ == "__main__":
    test_karthik_flow()
