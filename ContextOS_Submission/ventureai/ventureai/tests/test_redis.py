import sys
import os
# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis_client import cache_set, cache_get, cache_delete, set_hitl_pending, get_hitl_pending, resolve_hitl, get_hitl_decision

def test_redis_operations():
    print("--- Testing Redis Caching Operations ---")
    test_key = "test:candidate:123"
    test_data = {"name": "John Doe", "skills": ["Python", "Docker"]}
    
    # Set and Get
    cache_set(test_key, test_data, ttl=60)
    retrieved = cache_get(test_key)
    print(f"Cache Set/Get: {'PASSED' if retrieved == test_data else 'FAILED'} (Got: {retrieved})")
    
    # Delete
    cache_delete(test_key)
    retrieved_after_delete = cache_get(test_key)
    print(f"Cache Delete: {'PASSED' if retrieved_after_delete is None else 'FAILED'} (Got: {retrieved_after_delete})")
    
    print("\n--- Testing Redis HITL Operations ---")
    session_id = "test_session_abc123"
    hitl_payload = {"candidate_id": "cand_1", "action": "pitch_candidate"}
    
    set_hitl_pending(session_id, hitl_payload, ttl=60)
    pending = get_hitl_pending(session_id)
    print(f"HITL Pending Set/Get: {'PASSED' if pending == hitl_payload else 'FAILED'} (Got: {pending})")
    
    resolve_hitl(session_id, "approved")
    decision = get_hitl_decision(session_id)
    print(f"HITL Resolve/Decision: {'PASSED' if decision == 'approved' else 'FAILED'} (Got: {decision})")
    
    # Clean up
    cache_delete(f"hitl:{session_id}")
    cache_delete(f"hitl:{session_id}:decision")
    print("Cleanup Completed.")

if __name__ == "__main__":
    test_redis_operations()
