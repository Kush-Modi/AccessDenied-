import os
import sys
from datetime import datetime, timezone
import math
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.filters import load_ranking_config
from supabase_client import supabase

def calculate_recency_score(created_at_str: str) -> float:
    """Calculate exponential decay recency score between 0.0 and 1.0."""
    if not created_at_str:
        return 0.5
    try:
        created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - created_dt
        days_ago = max(0, delta.days)
        # Lambda = 0.02 (reaches ~0.37 after 50 days)
        return math.exp(-0.02 * days_ago)
    except Exception:
        return 0.5

def extract_importance_score(item: dict) -> float:
    """Extract importance score (0.0 to 1.0) from item importance labels."""
    meta = item.get("metadata") or {}
    importance = str(meta.get("importance", "")).lower()
    if "critical" in importance or "high" in importance:
        return 1.0
    if "medium" in importance:
        return 0.6
    if "low" in importance:
        return 0.2
    return 0.5

def calculate_business_signal_score(item: dict) -> float:
    """Calculate business signal weight based on keywords, type, and urgency markers."""
    score = 0.5
    text_to_check = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()
    
    # Check for strong business indicators
    critical_keywords = ["offer accepted", "hiring freeze", "placed", "hired", "counter offer", "critical", "urgent", "sign-off"]
    high_keywords = ["interview", "feedback", "screening", "pipeline", "scheduled", "match", "shortlist"]
    
    if any(k in text_to_check for k in critical_keywords):
        score = 1.0
    elif any(k in text_to_check for k in high_keywords):
        score = 0.8
    elif "ghosting" in text_to_check or "rejected" in text_to_check or "declined" in text_to_check:
        score = 0.3
        
    return score

def fetch_client_health(client_id: str) -> float:
    """Query client health score from Supabase. Default to 0.5."""
    if not client_id:
        return 0.5
    try:
        # Check clients table
        res = supabase.table("clients").select("account_health").eq("id", client_id).execute()
        if res.data and len(res.data) > 0:
            health = res.data[0].get("account_health")
            if health is not None:
                return float(health) / 100.0 # Scale 0-100 to 0.0-1.0
    except Exception:
        pass
    return 0.5

def fetch_placement_history_success(candidate_id: str, client_id: str) -> float:
    """Estimate historical placement success probability. Default to 0.5."""
    # If client/candidate has successful historical interviews or placements, score higher
    score = 0.5
    if not candidate_id and not client_id:
        return score
        
    try:
        # Check interview feedback or past logs
        if candidate_id:
            res = supabase.table("interview_feedback").select("rating").eq("candidate_id", candidate_id).execute()
            ratings = [r.get("rating") for r in res.data if r.get("rating") is not None]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                score = avg_rating / 5.0 # Scale 1-5 to 0.2-1.0
    except Exception:
        pass
    return score

def rank_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks items based on configured weights in config/ranking_config.yaml.
    Calculates final score and appends individual score signals for explainability.
    """
    config = load_ranking_config()
    weights = config.get("weights", {
        "semantic_similarity": 0.40,
        "business_signals": 0.20,
        "client_health": 0.15,
        "placement_history": 0.10,
        "recency": 0.10,
        "importance": 0.05
    })
    
    ranked_items = []
    # Collect unique client IDs for batch health lookup
    client_health_cache = {}
    
    for item in items:
        # 1. Semantic Similarity (0.0 to 1.0)
        semantic = float(item.get("similarity", 0.5))
        
        # 2. Recency (0.0 to 1.0)
        recency = calculate_recency_score(item.get("created_at"))
        
        # 3. Importance (0.0 to 1.0)
        importance = extract_importance_score(item)
        
        # 4. Business Signals (0.0 to 1.0)
        business = calculate_business_signal_score(item)
        
        # Fetch Client ID and Candidate ID from metadata or item
        meta = item.get("metadata") or {}
        client_id = meta.get("client_id") or meta.get("client") or (item.get("entity_id") if item.get("entity_type") == "client" else None)
        candidate_id = meta.get("candidate_id") or meta.get("candidate") or (item.get("entity_id") if item.get("entity_type") == "candidate" else None)
        
        # 5. Client Health (0.0 to 1.0)
        if client_id:
            if client_id not in client_health_cache:
                client_health_cache[client_id] = fetch_client_health(client_id)
            health = client_health_cache[client_id]
        else:
            health = 0.5
            
        # 6. Placement History Success (0.0 to 1.0)
        history = fetch_placement_history_success(candidate_id, client_id)
        
        # Calculate weighted final score
        final_score = (
            weights.get("semantic_similarity", 0.40) * semantic +
            weights.get("business_signals", 0.20) * business +
            weights.get("client_health", 0.15) * health +
            weights.get("placement_history", 0.10) * history +
            weights.get("recency", 0.10) * recency +
            weights.get("importance", 0.05) * importance
        )
        
        # Append scores back to item for Explainability
        item_ranked = item.copy()
        item_ranked["scores"] = {
            "semantic_similarity": semantic,
            "business_signals": business,
            "client_health": health,
            "placement_history": history,
            "recency": recency,
            "importance": importance,
            "final_score": final_score
        }
        ranked_items.append(item_ranked)
        
    # Sort by final score descending
    ranked_items.sort(key=lambda x: x["scores"]["final_score"], reverse=True)
    return ranked_items
