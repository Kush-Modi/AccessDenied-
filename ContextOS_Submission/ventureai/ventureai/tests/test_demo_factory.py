import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase
from demo_data.health_generator import calculate_client_health
from demo_data.priority_generator import calculate_job_priority

def test_health_generator_ranges():
    """Verify that the health calculator produces correct ranges under boundary conditions."""
    # Worst case
    low_health = calculate_client_health(
        last_contact_days=100,
        open_positions_count=0,
        placement_success_rate=0.0,
        recruiter_activity_count=0,
        recent_meetings_count=0
    )
    assert 0 <= low_health <= 100
    
    # Best case
    high_health = calculate_client_health(
        last_contact_days=2,
        open_positions_count=10,
        placement_success_rate=1.0,
        recruiter_activity_count=15,
        recent_meetings_count=5
    )
    assert high_health == 100

def test_priority_generator_labels():
    """Verify priority mapping for jobs."""
    p_critical = calculate_job_priority(client_health=20, urgency_level="high", job_age_days=5, recruiter_activity_count=0)
    assert p_critical == "Critical"
    
    p_low = calculate_job_priority(client_health=70, urgency_level="low", job_age_days=100, recruiter_activity_count=20)
    assert p_low in ["Medium", "Low"]

def test_database_relationships():
    """Verify relationships in Supabase and ensure no orphans or duplicates exist."""
    # 1. Fetch all records
    candidates = supabase.table("candidates").select("id").execute().data or []
    clients = supabase.table("clients").select("id, name, account_health").execute().data or []
    jobs = supabase.table("job_descriptions").select("id, client_id, description_text").execute().data or []
    
    cand_ids = {c["id"] for c in candidates}
    client_ids = {c["id"] for c in clients}
    job_ids = {j["id"] for j in jobs}
    
    assert len(candidates) > 0, "Candidates table is empty"
    assert len(clients) > 0, "Clients table is empty"
    assert len(jobs) > 0, "Job Descriptions table is empty"
    
    # 2. Check health scores valid
    for client in clients:
        health = client.get("account_health")
        assert health is not None, f"Client {client['name']} has no account health"
        assert 0 <= health <= 100, f"Client health score {health} is out of bounds [0, 100]"
        
    # 3. Check priorities assigned in description_text
    for job in jobs:
        desc = job.get("description_text", "")
        assert "[Priority:" in desc, f"Job Description does not contain priority prefix: {desc}"
        
    # 4. Check no orphans in recruiter_notes
    notes = supabase.table("recruiter_notes").select("*").execute().data or []
    for note in notes:
        assert note["candidate_id"] in cand_ids, f"Orphan recruiter note found: candidate {note['candidate_id']} does not exist"
        
    # 5. Check no orphans in meeting_notes
    meetings = supabase.table("meeting_notes").select("*").execute().data or []
    for mtg in meetings:
        assert mtg["client_id"] in client_ids, f"Orphan meeting note found: client {mtg['client_id']} does not exist"
        if mtg.get("candidate_id"):
            assert mtg["candidate_id"] in cand_ids, f"Orphan meeting note found: candidate {mtg['candidate_id']} does not exist"
            
    # 6. Check no orphans in crm_updates
    crm = supabase.table("crm_updates").select("*").execute().data or []
    for update in crm:
        assert update["client_id"] in client_ids, f"Orphan CRM update found: client {update['client_id']} does not exist"
        
    # 7. Check no orphans in emails
    emails = supabase.table("emails").select("*").execute().data or []
    assert len(emails) > 0, "No emails generated"
    
    # 8. Check no orphans in interview_feedback
    feedbacks = supabase.table("interview_feedback").select("*").execute().data or []
    for fb in feedbacks:
        assert fb["candidate_id"] in cand_ids, f"Orphan feedback found: candidate {fb['candidate_id']} does not exist"
        assert fb["jd_id"] in job_ids, f"Orphan feedback found: job {fb['jd_id']} does not exist"
        assert 1 <= fb["rating"] <= 5, f"Feedback rating {fb['rating']} is out of bounds [1, 5]"

    # 9. Verify no duplicates in knowledge_items
    ki_items = supabase.table("knowledge_items").select("id").execute().data or []
    ki_ids = [ki["id"] for ki in ki_items]
    assert len(ki_ids) == len(set(ki_ids)), "Duplicate UUIDs found in knowledge_items table!"
