import sys
import os
from typing import Dict, Any, List, Optional
from memory.repository import MemoryRepository
from memory.learning import FeedbackLearner

class PlannerMemory:
    @staticmethod
    def get_memory_context(
        candidate_id: str,
        client_id: str,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Retrieves feedback history matching this candidate, client, or job,
        and returns the computed learning score/explanation.
        """
        # Query database history
        history = MemoryRepository.get_feedback_history(
            candidate_id=candidate_id,
            client_id=client_id,
            job_id=job_id
        )
        
        # Run learning analytics
        analysis = FeedbackLearner.analyze_history(history)
        
        # Add metadata traces
        history_trace = []
        for h in history:
            history_trace.append({
                "recommendation_id": h.get("recommendation_id"),
                "decision": h.get("recruiter_decision"),
                "outcome": h.get("outcome"),
                "timestamp": h.get("created_at")
            })
            
        analysis["history_trace"] = history_trace
        analysis["history_count"] = len(history)
        return analysis
