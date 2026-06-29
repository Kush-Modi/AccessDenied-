import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase

class MemoryRepository:
    @staticmethod
    def save_feedback(
        candidate_id: str,
        client_id: str,
        job_id: str,
        recruiter_decision: str,
        recommendation_id: Optional[str] = None,
        decision_reason: Optional[str] = None,
        historical_confidence: Optional[float] = None,
        outcome: str = "pending",
        placement_success: bool = False,
        placement_failure: bool = False,
        feedback_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Saves a new recommendation feedback record to the database."""
        payload = {
            "recommendation_id": recommendation_id or str(os.urandom(8).hex()),
            "candidate_id": candidate_id,
            "client_id": client_id,
            "job_id": job_id,
            "recruiter_decision": recruiter_decision.lower(),
            "decision_reason": decision_reason,
            "outcome": outcome.lower(),
            "placement_success": placement_success,
            "placement_failure": placement_failure,
            "feedback_notes": feedback_notes,
            "historical_confidence": historical_confidence,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            result = supabase.table("planner_feedback").insert(payload).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            sys.stderr.write(f"Error saving planner feedback to Supabase: {e}\n")
            return {}

    @staticmethod
    def update_outcome(
        recommendation_id: str,
        outcome: str,
        success: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates the placement outcome of a recommendation."""
        payload = {
            "outcome": outcome.lower(),
            "placement_success": success,
            "placement_failure": not success,
            "feedback_notes": notes,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            result = supabase.table("planner_feedback")\
                .update(payload)\
                .eq("recommendation_id", recommendation_id)\
                .execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            sys.stderr.write(f"Error updating outcome for recommendation {recommendation_id}: {e}\n")
            return {}

    @staticmethod
    def get_feedback_history(
        candidate_id: Optional[str] = None,
        client_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries feedback history from the database."""
        try:
            query = supabase.table("planner_feedback").select("*")
            
            if candidate_id:
                query = query.eq("candidate_id", candidate_id)
            if client_id:
                query = query.eq("client_id", client_id)
            if job_id:
                query = query.eq("job_id", job_id)
                
            result = query.execute()
            return result.data or []
        except Exception as e:
            sys.stderr.write(f"Error fetching feedback history: {e}\n")
            return []
