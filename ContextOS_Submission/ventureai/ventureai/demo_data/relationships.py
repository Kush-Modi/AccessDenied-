import hashlib
import uuid
import random
from datetime import datetime, timedelta
from demo_data.templates import SCENARIO_TEMPLATES, INTERVIEW_FEEDBACK_TEMPLATES, RECRUITER_NAMES

def generate_deterministic_uuid(seed_str: str) -> str:
    """Generate a deterministic UUID v4 string from a seed string."""
    hash_obj = hashlib.sha256(seed_str.encode('utf-8'))
    # Use first 16 bytes for UUID
    return str(uuid.UUID(bytes=hash_obj.digest()[:16]))

def generate_interaction_chain(
    candidate: dict,
    job: dict,
    client: dict,
    scenario: str,
    base_date: datetime
) -> dict:
    """
    Generate a connected set of recruitment interactions for a candidate-job-client chain,
    shaped by a specific scenario.
    """
    candidate_id = candidate["id"]
    candidate_name = candidate["name"]
    job_id = job["id"]
    job_title = job["title"]
    client_id = client["id"]
    client_name = client["name"]
    client_contact = client.get("contact_name", "Hiring Manager")
    
    # Pick a random recruiter name deterministically based on candidate ID
    random.seed(candidate_id)
    recruiter_name = random.choice(RECRUITER_NAMES)
    
    # Templates for the specific scenario
    templates = SCENARIO_TEMPLATES.get(scenario, SCENARIO_TEMPLATES["Urgent Hiring"])
    
    # Generate timelines spaced out by days
    dates = [base_date + timedelta(days=i) for i in range(1, 6)]
    
    chain = {
        "recruiter_notes": [],
        "meeting_notes": [],
        "crm_updates": [],
        "emails": [],
        "interview_feedback": [],
        "placements": []
    }
    
    # 1. Recruiter Notes (2-5 notes)
    notes_list = templates["recruiter_notes"]
    num_notes = min(len(notes_list), random.randint(2, 5))
    for i in range(num_notes):
        note_text = notes_list[i]
        note_id = generate_deterministic_uuid(f"note_{candidate_id}_{job_id}_{scenario}_{i}")
        chain["recruiter_notes"].append({
            "id": note_id,
            "candidate_id": candidate_id,
            "notes": note_text,
            "created_at": dates[i].isoformat()
        })
        
    # 2. Meeting Notes
    meeting_list = templates["meeting_notes"]
    meeting_text = random.choice(meeting_list)
    meeting_id = generate_deterministic_uuid(f"meeting_{candidate_id}_{job_id}_{scenario}")
    chain["meeting_notes"].append({
        "id": meeting_id,
        "client_id": client_id,
        "candidate_id": candidate_id,
        "meeting_date": dates[1].strftime("%Y-%m-%d"),
        "notes": f"Meeting regarding {candidate_name} for role {job_title}: {meeting_text}",
        "created_at": dates[1].isoformat()
    })
    
    # 3. CRM Updates
    crm_list = templates["crm_updates"]
    crm_text = random.choice(crm_list)
    crm_id = generate_deterministic_uuid(f"crm_{candidate_id}_{job_id}_{scenario}")
    chain["crm_updates"].append({
        "id": crm_id,
        "client_id": client_id,
        "update_text": f"CRM Update: {crm_text} (Target Job: {job_title}, Candidate: {candidate_name})",
        "created_at": dates[2].isoformat()
    })
    
    # 4. Emails
    email_templates = templates["emails"]
    for i, t in enumerate(email_templates):
        subj = t["subject"].replace("[Candidate Name]", candidate_name).replace("[Job Title]", job_title)
        body = t["body"].replace("[Client Contact]", client_contact) \
                       .replace("[Job Title]", job_title) \
                       .replace("[Candidate Name]", candidate_name) \
                       .replace("[Experience Years]", str(candidate.get("experience_years", 5))) \
                       .replace("[Recruiter Name]", recruiter_name) \
                       .replace("[Placement Date]", dates[4].strftime("%Y-%m-%d"))
        
        email_id = generate_deterministic_uuid(f"email_{candidate_id}_{job_id}_{scenario}_{i}")
        chain["emails"].append({
            "id": email_id,
            "sender": f"{recruiter_name.lower().replace(' ', '.')}@xlventures.com",
            "recipient": f"hiring@{client_name.lower().replace(' ', '')}.com",
            "subject": subj,
            "body": body,
            "sent_at": dates[3].isoformat()
        })
        
    # 5. Interview Feedback
    # Deterministic selection based on scenario
    feedback_idx = random.randint(0, len(INTERVIEW_FEEDBACK_TEMPLATES) - 1)
    fb_temp = INTERVIEW_FEEDBACK_TEMPLATES[feedback_idx]
    
    # Adjust feedback based on scenario
    if scenario == "Candidate Ghosting":
        fb_text = "Failed to attend scheduled technical round. Candidate ghosted completely."
        rating = 1
    elif scenario == "Offer Accepted":
        fb_text = "Excellent interview performance. Technical and cultural fit are top tier."
        rating = 5
    elif scenario == "Offer Declined":
        fb_text = "Interview feedback was positive but candidate chose to pursue competing offer."
        rating = 4
    else:
        fb_text = fb_temp["feedback"]
        rating = fb_temp["rating"]
        
    fb_id = generate_deterministic_uuid(f"fb_{candidate_id}_{job_id}_{scenario}")
    chain["interview_feedback"].append({
        "id": fb_id,
        "candidate_id": candidate_id,
        "jd_id": job_id,
        "feedback": fb_text,
        "rating": rating,
        "created_at": dates[3].isoformat()
    })
    
    # 6. Placement History
    # Match outcomes with scenarios
    if scenario == "Offer Accepted":
        success = True
        notes = "Candidate successfully placed and started. Retention rate high."
    elif scenario in ["Offer Declined", "Candidate Ghosting", "Hiring Freeze", "Position Closed"]:
        success = False
        notes = f"Placement unsuccessful due to scenario: {scenario}"
    else:
        # Default mix
        success = (random.random() > 0.4)
        notes = "Completed placement evaluation lifecycle."
        
    placement_id = generate_deterministic_uuid(f"placement_{candidate_id}_{job_id}_{scenario}")
    chain["placements"].append({
        "id": placement_id,
        "candidate_id": candidate_id,
        "client_id": client_id,
        "jd_id": job_id,
        "placement_date": dates[4].strftime("%Y-%m-%d"),
        "success": success,
        "notes": notes
    })
    
    return chain
