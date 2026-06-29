import sys
import os
from typing import Dict, Any, Optional
from memory.repository import MemoryRepository

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import redis_client

class FeedbackManager:
    @staticmethod
    def log_recruiter_decision(
        candidate_id: str,
        client_id: str,
        job_id: str,
        decision: str, # approved, rejected, modified, ignored, expired, cancelled
        recommendation_id: Optional[str] = None,
        reason: Optional[str] = None,
        confidence: float = 0.0,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Logs recruiter decision (approved/rejected/etc.) and updates memory layer."""
        decision_clean = decision.lower().strip()
        
        # Outcome defaults based on decision
        outcome = "pending"
        success = False
        failure = False
        
        if decision_clean in ["rejected", "cancelled"]:
            outcome = "rejected"
            failure = True
            
        record = MemoryRepository.save_feedback(
            candidate_id=candidate_id,
            client_id=client_id,
            job_id=job_id,
            recruiter_decision=decision_clean,
            recommendation_id=recommendation_id,
            decision_reason=reason,
            historical_confidence=confidence,
            outcome=outcome,
            placement_success=success,
            placement_failure=failure,
            feedback_notes=notes
        )
        
        # Optionally invalidate candidate cache in Redis to trigger re-evaluation
        try:
            redis_client.r.delete(f"nba:{candidate_id}")
        except:
            pass
            
        return record

    @staticmethod
    def log_placement_outcome(
        recommendation_id: str,
        outcome: str, # success, failure
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Logs placement outcome (success/failure) of a previously approved recommendation."""
        success = outcome.lower() == "success"
        record = MemoryRepository.update_outcome(
            recommendation_id=recommendation_id,
            outcome=outcome,
            success=success,
            notes=notes
        )
        return record
