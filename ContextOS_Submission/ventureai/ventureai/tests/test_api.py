import sys
import os
from fastapi.testclient import TestClient

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override standard python command to use active venv python interpreter
import mcp_client
mcp_client.SERVER_PARAMS.command = sys.executable

from main import app
from redis_client import r

client = TestClient(app)

def test_full_api_workflow():
    # Clear Redis cache for candidate to make test hermetic and bypass caching
    candidate_id = "a2f52625-84e2-4367-abc6-9eccca7b5e54"
    if r:
        r.delete(f"nba:{candidate_id}")
    
    # 1. Test /health
    print("\n--- Testing GET /health ---")
    res = client.get("/health")
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 200
    
    # 2. Test /analyze
    print("\n--- Testing POST /analyze ---")
    res = client.post("/analyze", json={"candidate_id": candidate_id})
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 200
    data = res.json()
    session_id = data["session_id"]
    
    # 3. Test /hitl/pending/{session_id}
    print(f"\n--- Testing GET /hitl/pending/{session_id} ---")
    res = client.get(f"/hitl/pending/{session_id}")
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 200
    
    # 4. Test /hitl/respond
    print("\n--- Testing POST /hitl/respond ---")
    res = client.post("/hitl/respond", json={"session_id": session_id, "decision": "approved"})
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 200
    
    # 5. Test /nba/queue
    print("\n--- Testing GET /nba/queue ---")
    res = client.get("/nba/queue")
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 200

if __name__ == "__main__":
    test_full_api_workflow()
