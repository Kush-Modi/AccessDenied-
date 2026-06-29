import sys
import os
import random
from datetime import datetime, timezone
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase
from redis_client import log_session
from demo_data.scenarios import SCENARIOS, get_scenario_metadata
from demo_data.health_generator import calculate_client_health
from demo_data.priority_generator import calculate_job_priority
from demo_data.relationships import generate_interaction_chain, generate_deterministic_uuid

def log_factory_event(message: str):
    """Log to stdout and Redis logs."""
    timestamp = datetime.now(timezone.utc).isoformat()
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    try:
        log_session("demo_data_factory", formatted)
    except Exception as e:
        print(f"Failed to log to Redis: {e}")

def run_factory():
    log_factory_event("Starting Demo Data Factory...")
    
    # 1. Fetch existing core entities from Supabase
    try:
        cand_res = supabase.table("candidates").select("*").execute()
        candidates = cand_res.data or []
        log_factory_event(f"Loaded {len(candidates)} candidates from Supabase.")
        
        client_res = supabase.table("clients").select("*").execute()
        clients = client_res.data or []
        log_factory_event(f"Loaded {len(clients)} clients from Supabase.")
        
        job_res = supabase.table("job_descriptions").select("*").execute()
        jobs = job_res.data or []
        log_factory_event(f"Loaded {len(jobs)} job descriptions from Supabase.")
    except Exception as e:
        log_factory_event(f"Error fetching core data: {e}")
        return
        
    if not candidates or not clients or not jobs:
        log_factory_event("Cannot generate data: candidates, clients, or jobs tables are empty.")
        return

    # Map clients and jobs for easy lookup
    clients_map = {c["id"]: c for c in clients}
    jobs_by_client = {}
    for j in jobs:
        c_id = j["client_id"]
        if c_id not in jobs_by_client:
            jobs_by_client[c_id] = []
        jobs_by_client[c_id].append(j)
        
    # Track statistics for health calculation later
    client_stats = {
        c["id"]: {
            "last_contact_days": 30, # Default
            "placement_success_count": 0,
            "placement_total_count": 0,
            "recruiter_activity_count": 0,
            "meetings_count": 0
        }
        for c in clients
    }
    
    generated_recruiter_notes = []
    generated_meeting_notes = []
    generated_crm_updates = []
    generated_emails = []
    generated_interview_feedback = []
    generated_placements = []
    generated_customer_interactions = []
    generated_knowledge_items = []
    
    base_date = datetime.now(timezone.utc)
    
    # 2. Pair each candidate with jobs and generate scenario-driven interactions
    log_factory_event("Generating connected interaction chains...")
    for idx, candidate in enumerate(candidates):
        # Pick scenario deterministically based on candidate index
        scenario = SCENARIOS[idx % len(SCENARIOS)]
        scenario_meta = get_scenario_metadata(scenario)
        
        # Pick job and client deterministically
        job = jobs[idx % len(jobs)]
        client_id = job["client_id"]
        client = clients_map.get(client_id)
        
        if not client:
            continue
            
        log_factory_event(f"Generating scenario '{scenario}' for candidate {candidate['name']} and job {job['title']} (Client: {client['name']})")
        
        chain = generate_interaction_chain(candidate, job, client, scenario, base_date)
        
        # Update client statistics
        stats = client_stats[client_id]
        stats["meetings_count"] += len(chain["meeting_notes"])
        stats["recruiter_activity_count"] += len(chain["recruiter_notes"])
        
        # Placements
        for p in chain["placements"]:
            stats["placement_total_count"] += 1
            if p["success"]:
                stats["placement_success_count"] += 1
            generated_placements.append(p)
            
            # Add placement to knowledge items
            ki_id = generate_deterministic_uuid(f"ki_placement_{p['id']}")
            generated_knowledge_items.append({
                "id": ki_id,
                "type": "placement",
                "source": "placement_system",
                "entity_type": "candidate",
                "entity_id": candidate["id"],
                "title": f"Placement in {job['title']}",
                "summary": p["notes"],
                "content": f"Candidate was evaluated for {job['title']} at {client['name']}. Success: {p['success']}.",
                "metadata": {
                    "client_id": client_id,
                    "job_id": job["id"],
                    "success": p["success"],
                    "source": "placement_system",
                    "reason": "Placement outcome verification",
                    "importance": "high" if p["success"] else "medium",
                    "confidence": 1.0
                },
                "created_at": p["placement_date"] + "T00:00:00Z"
            })
            
        # Recruiter notes
        for n in chain["recruiter_notes"]:
            generated_recruiter_notes.append(n)
            # Add to knowledge items
            ki_id = generate_deterministic_uuid(f"ki_rec_note_{n['id']}")
            generated_knowledge_items.append({
                "id": ki_id,
                "type": "recruiter_note",
                "source": "recruiter_journal",
                "entity_type": "candidate",
                "entity_id": candidate["id"],
                "title": "Recruiter Profile Observation",
                "summary": n["notes"][:60] + "...",
                "content": n["notes"],
                "metadata": {
                    "source": "recruiter_journal",
                    "reason": "Recruiter-candidate intake discussion notes",
                    "importance": "medium",
                    "confidence": 0.90
                },
                "created_at": n["created_at"]
            })
            
        # Meeting notes
        for m in chain["meeting_notes"]:
            generated_meeting_notes.append(m)
            # Add to knowledge items
            ki_id = generate_deterministic_uuid(f"ki_meeting_{m['id']}")
            generated_knowledge_items.append({
                "id": ki_id,
                "type": "meeting",
                "source": "meeting_scheduler",
                "entity_type": "client",
                "entity_id": client_id,
                "title": f"Account Status Meeting - {job['title']}",
                "summary": m["notes"][:60] + "...",
                "content": m["notes"],
                "metadata": {
                    "candidate_id": candidate["id"],
                    "job_id": job["id"],
                    "source": "meeting_scheduler",
                    "reason": "Client sync meeting regarding pipelines",
                    "importance": "high",
                    "confidence": 0.95
                },
                "created_at": m["created_at"]
            })
            # Add to customer interactions
            generated_customer_interactions.append({
                "id": m["id"],
                "client_id": client_id,
                "candidate_id": candidate["id"],
                "interaction_date": m["meeting_date"],
                "type": "meeting",
                "notes": m["notes"]
            })
            
        # CRM updates
        for c in chain["crm_updates"]:
            generated_crm_updates.append(c)
            # Add to knowledge items
            ki_id = generate_deterministic_uuid(f"ki_crm_{c['id']}")
            generated_knowledge_items.append({
                "id": ki_id,
                "type": "crm",
                "source": "crm_salesforce",
                "entity_type": "client",
                "entity_id": client_id,
                "title": "CRM Activity Log",
                "summary": c["update_text"][:60] + "...",
                "content": c["update_text"],
                "metadata": {
                    "source": "crm_salesforce",
                    "reason": "Client relationship follow-up note",
                    "importance": "medium",
                    "confidence": 0.85
                },
                "created_at": c["created_at"]
            })
            # Add to customer interactions
            generated_customer_interactions.append({
                "id": c["id"],
                "client_id": client_id,
                "candidate_id": candidate["id"],
                "interaction_date": c["created_at"][:10],
                "type": "crm",
                "notes": c["update_text"]
            })
            
        # Emails
        for e in chain["emails"]:
            generated_emails.append(e)
            # Add to knowledge items
            ki_id = generate_deterministic_uuid(f"ki_email_{e['id']}")
            generated_knowledge_items.append({
                "id": ki_id,
                "type": "email",
                "source": "outlook_mail",
                "entity_type": "candidate",
                "entity_id": candidate["id"],
                "title": e["subject"],
                "summary": f"Email to hiring contact: {e['subject']}",
                "content": e["body"],
                "metadata": {
                    "recipient": e["recipient"],
                    "sender": e["sender"],
                    "source": "outlook_mail",
                    "reason": "Client interaction pipeline exchange",
                    "importance": "high",
                    "confidence": 1.0
                },
                "created_at": e["sent_at"]
            })
            # Add to customer interactions
            generated_customer_interactions.append({
                "id": e["id"],
                "client_id": client_id,
                "candidate_id": candidate["id"],
                "interaction_date": e["sent_at"][:10],
                "type": "email",
                "notes": f"Subject: {e['subject']}\n\n{e['body']}"
            })
            
        # Interview feedback
        for f in chain["interview_feedback"]:
            generated_interview_feedback.append(f)
            # Add to knowledge items
            ki_id = generate_deterministic_uuid(f"ki_fb_{f['id']}")
            generated_knowledge_items.append({
                "id": ki_id,
                "type": "interview_feedback",
                "source": "interview_portal",
                "entity_type": "candidate",
                "entity_id": candidate["id"],
                "title": f"Interview Feedback - {job['title']}",
                "summary": f"Rating {f['rating']}/5: {f['feedback'][:50]}...",
                "content": f["feedback"],
                "metadata": {
                    "job_id": f["jd_id"],
                    "rating": f["rating"],
                    "source": "interview_portal",
                    "reason": "Technical interview outcome panel evaluation",
                    "importance": "high",
                    "confidence": 0.95
                },
                "created_at": f["created_at"]
            })

    # 3. Calculate Client Health & Job Priorities
    log_factory_event("Calculating Client Health scores...")
    updated_clients = []
    for c in clients:
        stats = client_stats[c["id"]]
        # Success rate
        success_rate = stats["placement_success_count"] / stats["placement_total_count"] if stats["placement_total_count"] > 0 else 0.5
        
        # Calculate health (0-100)
        health_score = calculate_client_health(
            last_contact_days=10 if stats["meetings_count"] > 0 else 45,
            open_positions_count=len(jobs_by_client.get(c["id"], [])),
            placement_success_rate=success_rate,
            recruiter_activity_count=stats["recruiter_activity_count"],
            recent_meetings_count=stats["meetings_count"]
        )
        
        updated_clients.append({
            "id": c["id"],
            "name": c["name"],
            "industry": c["industry"],
            "account_health": health_score,
            "last_contact_date": base_date.strftime("%Y-%m-%d"),
            "open_roles_count": len(jobs_by_client.get(c["id"], []))
        })
        log_factory_event(f"Client {c['name']}: health score calculated as {health_score}")
        
    log_factory_event("Calculating Job Priorities...")
    updated_jobs = []
    for j in jobs:
        c_id = j["client_id"]
        c_health = next((uc["account_health"] for uc in updated_clients if uc["id"] == c_id), 50)
        c_stats = client_stats.get(c_id, {})
        
        # Determine priority (Critical, High, Medium, Low)
        priority = calculate_job_priority(
            client_health=c_health,
            urgency_level="high" if c_health < 40 else "medium",
            job_age_days=10,
            recruiter_activity_count=c_stats.get("recruiter_activity_count", 0)
        )
        
        # Store in description by prefixing [Priority: Level] safely
        desc = j.get("description_text", "")
        # Remove any existing priority prefix to prevent duplicate tagging on multiple runs
        if desc.startswith("[Priority:"):
            desc = desc.split("] ", 1)[1] if "] " in desc else desc
            
        updated_desc = f"[Priority: {priority}] {desc}"
        
        updated_jobs.append({
            "id": j["id"],
            "client_id": j["client_id"],
            "title": j["title"],
            "required_skills": j.get("required_skills", []),
            "location": j.get("location"),
            "salary_range": j.get("salary_range"),
            "status": j.get("status"),
            "description_text": updated_desc
        })
        log_factory_event(f"Job {j['title']}: priority evaluated as {priority}")

    # 4. Upsert everything to Supabase to prevent duplicates
    log_factory_event("Uploading data to Supabase...")
    try:
        # Core entity updates
        supabase.table("clients").upsert(updated_clients).execute()
        log_factory_event(f"Upserted {len(updated_clients)} updated client records.")
        
        supabase.table("job_descriptions").upsert(updated_jobs).execute()
        log_factory_event(f"Upserted {len(updated_jobs)} updated job descriptions.")
        
        # Interaction tables
        if generated_recruiter_notes:
            supabase.table("recruiter_notes").upsert(generated_recruiter_notes).execute()
            log_factory_event(f"Upserted {len(generated_recruiter_notes)} recruiter notes.")
            
        if generated_meeting_notes:
            supabase.table("meeting_notes").upsert(generated_meeting_notes).execute()
            log_factory_event(f"Upserted {len(generated_meeting_notes)} meeting notes.")
            
        if generated_crm_updates:
            supabase.table("crm_updates").upsert(generated_crm_updates).execute()
            log_factory_event(f"Upserted {len(generated_crm_updates)} CRM updates.")
            
        if generated_emails:
            supabase.table("emails").upsert(generated_emails).execute()
            log_factory_event(f"Upserted {len(generated_emails)} emails.")
            
        if generated_interview_feedback:
            supabase.table("interview_feedback").upsert(generated_interview_feedback).execute()
            log_factory_event(f"Upserted {len(generated_interview_feedback)} interview feedback records.")
            
        if generated_placements:
            supabase.table("placements").upsert(generated_placements).execute()
            log_factory_event(f"Upserted {len(generated_placements)} placement history records.")
            
        if generated_customer_interactions:
            supabase.table("customer_interactions").upsert(generated_customer_interactions).execute()
            log_factory_event(f"Upserted {len(generated_customer_interactions)} customer interactions.")
            
        if generated_knowledge_items:
            supabase.table("knowledge_items").upsert(generated_knowledge_items).execute()
            log_factory_event(f"Upserted {len(generated_knowledge_items)} Universal Knowledge items.")
            
        log_factory_event("Demo Data Factory completed successfully!")
        
        # Clear Redis cache for candidates and clients to ensure fresh data retrieval
        try:
            from redis_client import r
            client_keys = r.keys("client:*")
            cand_keys = r.keys("cand:*")
            if client_keys:
                r.delete(*client_keys)
            if cand_keys:
                r.delete(*cand_keys)
            log_factory_event("Cleared Redis cache for clients and candidates.")
        except Exception as cache_err:
            log_factory_event(f"Warning: Failed to clear Redis cache: {cache_err}")
    except Exception as e:
        log_factory_event(f"Database error during upsert: {e}")

if __name__ == "__main__":
    run_factory()
