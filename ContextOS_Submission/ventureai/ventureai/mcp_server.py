import os
import json
import re
from mcp.server.fastmcp import FastMCP
from supabase_client import supabase
from redis_client import cache_get, cache_set
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("recruiter-mcp")

@mcp.tool()
def get_candidate_profile(candidate_id: str) -> dict:
    """Get candidate profile by ID. Checks Redis cache first, then Supabase."""
    cache_key = f"cand:{candidate_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    result = supabase.table("candidates").select("*").eq("id", candidate_id).single().execute()
    data = result.data
    if data:
        cache_set(cache_key, data, ttl=600)
    return data or {}

@mcp.tool()
def get_client_account_health(client_id: str) -> dict:
    """Get client account health and metadata. Cached in Redis."""
    cache_key = f"client:{client_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    result = supabase.table("clients").select("*").eq("id", client_id).single().execute()
    data = result.data
    if data:
        data["account_health_score"] = data.get("account_health", 100)
        cache_set(cache_key, data, ttl=600)
    return data or {}

@mcp.tool()
def search_job_descriptions(query_skills: str) -> list:
    """Search open JDs by required skills (comma-separated). Returns top 5 matches."""
    # Safety: always work with a short keyword list
    if len(query_skills) > 300:
        query_skills = query_skills[:300]
    
    result = supabase.table("job_descriptions").select("*, clients(name)").eq("status", "open").execute()
    jobs = result.data or []
    if not jobs:
        return []

    # Build candidate skill tokens for matching
    skill_tokens = [s.strip().lower() for s in re.split(r"[,;/]", query_skills) if s.strip()]

    # Synonym map for common abbreviations
    synonyms = {
        "ml": "machine learning", "ai": "artificial intelligence",
        "nlp": "natural language processing", "cv": "computer vision",
        "k8s": "kubernetes", "tf": "terraform", "js": "javascript",
        "ts": "typescript", "py": "python", "sec": "security",
        "pentest": "penetration testing", "soc": "security operations",
        "iam": "identity access management",
    }
    expanded_tokens = set(skill_tokens)
    for tok in skill_tokens:
        if tok in synonyms:
            expanded_tokens.add(synonyms[tok])

    matched = []
    for job in jobs:
        req_skills = [r.lower() for r in job.get("required_skills", [])]
        if not req_skills:
            continue

        # Count exact + partial overlaps
        exact = sum(1 for s in expanded_tokens if s in req_skills)
        partial = sum(
            1 for s in expanded_tokens
            for r in req_skills
            if s in r or r in s
        ) - exact  # avoid double-counting

        score = min(1.0, (exact + 0.5 * partial) / max(len(req_skills), 1))

        if score > 0.0:
            job["match_score"] = round(score, 3)
            matched.append(job)

    matched.sort(key=lambda x: x["match_score"], reverse=True)
    return matched[:5]


@mcp.tool()
def get_placement_history(candidate_id: str = None, client_id: str = None) -> list:
    """Get past placements for candidate or client from Supabase."""
    q = supabase.table("placements").select("*, candidates(name), clients(name), job_descriptions(title)")
    if candidate_id:
        q = q.eq("candidate_id", candidate_id)
    if client_id:
        q = q.eq("client_id", client_id)
    result = q.execute()
    return result.data or []

@mcp.tool()
def log_recruiter_action(action_type: str, target_id: str, target_type: str, reason: str, recruiter_decision: str) -> dict:
    """Log a recruiter action to the memory layer in Supabase."""
    payload = {
        "action_type": action_type,
        "target_id": target_id,
        "target_type": target_type,
        "reason": reason,
        "recruiter_decision": recruiter_decision,
    }
    result = supabase.table("recruiter_actions").insert(payload).execute()
    return result.data[0] if result.data else {}

# --- New Universal Knowledge Layer Tools ---
_knowledge_service = None

def _get_knowledge_service():
    global _knowledge_service
    if _knowledge_service is None:
        from knowledge.knowledge_service import KnowledgeService
        _knowledge_service = KnowledgeService()
    return _knowledge_service

@mcp.tool()
def search_meeting_notes(client_id: str = None, candidate_id: str = None) -> list:
    """Search meeting notes by client_id or candidate_id."""
    ks = _get_knowledge_service()
    notes = ks.get_meeting_notes(client_id=client_id, candidate_id=candidate_id)
    return [n.dict() for n in notes]

@mcp.tool()
def search_crm_updates(client_id: str = None) -> list:
    """Search CRM activity updates by client_id."""
    ks = _get_knowledge_service()
    updates = ks.get_crm_updates(client_id=client_id)
    return [u.dict() for u in updates]

@mcp.tool()
def search_recruiter_notes(candidate_id: str = None) -> list:
    """Search recruiter notes by candidate_id."""
    ks = _get_knowledge_service()
    notes = ks.get_recruiter_notes(candidate_id=candidate_id)
    return [n.dict() for n in notes]

@mcp.tool()
def search_interview_feedback(candidate_id: str = None, jd_id: str = None) -> list:
    """Search interview feedback by candidate_id or jd_id."""
    ks = _get_knowledge_service()
    feedback = ks.get_interview_feedback(candidate_id=candidate_id, jd_id=jd_id)
    return [f.dict() for f in feedback]

@mcp.tool()
def search_emails(sender: str = None, recipient: str = None) -> list:
    """Search emails by sender or recipient address."""
    ks = _get_knowledge_service()
    emails = ks.get_emails(sender=sender, recipient=recipient)
    return [e.dict() for e in emails]

@mcp.tool()
def get_candidate_knowledge(candidate_id: str) -> dict:
    """Get structured knowledge context for a candidate."""
    # Convert datetime values to ISO format strings for JSON compatibility
    ks = _get_knowledge_service()
    context = ks.get_candidate_knowledge_context(candidate_id)
    # Convert datetime fields to strings
    for category in ["meeting_notes", "emails", "crm_updates", "playbooks", "recruiter_notes"]:
        if category in context:
            for item in context[category]:
                for key, val in item.items():
                    if hasattr(val, "isoformat"):
                        item[key] = val.isoformat()
    return context


if __name__ == "__main__":
    mcp.run()