from typing import List, Dict, Any

class FeedbackLearner:
    @staticmethod
    def analyze_history(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes historical decisions to calculate memory scores, learning scores,
        success rates, and generates an explanation.
        """
        if not records:
            return {
                "memory_score": 0.5,
                "learning_score": 0.0,
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "explanation": "No prior recruiter feedback history exists for this context."
            }
            
        approvals = [r for r in records if r.get("recruiter_decision") == "approved"]
        rejections = [r for r in records if r.get("recruiter_decision") == "rejected"]
        
        successes = [r for r in records if r.get("placement_success")]
        failures = [r for r in records if r.get("placement_failure")]
        
        total_decisions = len(approvals) + len(rejections)
        total_placements = len(successes) + len(failures)
        
        success_rate = len(successes) / total_placements if total_placements > 0 else 0.0
        failure_rate = len(failures) / total_placements if total_placements > 0 else 0.0
        
        # Calculate Learning Score adjustment
        learning_adjustment = 0.0
        explanations = []
        
        # 1. Learn from rejections
        if len(rejections) > 0:
            penalty = -0.15 * len(rejections)
            penalty = max(penalty, -0.40) # cap penalty
            learning_adjustment += penalty
            explanations.append(f"Penalized confidence by {penalty:.2f} due to {len(rejections)} past rejection(s).")
            
        # 2. Learn from placement successes
        if len(successes) > 0:
            boost = 0.10 * len(successes)
            boost = min(boost, 0.30) # cap boost
            learning_adjustment += boost
            explanations.append(f"Boosted confidence by {boost:.2f} due to {len(successes)} successful placement(s).")
            
        # 3. Learn from placement failures
        if len(failures) > 0:
            penalty = -0.20 * len(failures)
            penalty = max(penalty, -0.40)
            learning_adjustment += penalty
            explanations.append(f"Penalized confidence by {penalty:.2f} due to {len(failures)} placement failure(s).")
            
        # Calculate Memory Score (normalized to 0-1 range)
        # Default is 0.5; positive experience drives it up, negative drives it down.
        memory_score = 0.5 + (learning_adjustment / 2.0)
        memory_score = max(0.0, min(1.0, memory_score))
        
        explanation_str = " | ".join(explanations) if explanations else "Prior interactions analyzed, no major score adjustments applied."
        
        return {
            "memory_score": memory_score,
            "learning_score": learning_adjustment,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "explanation": explanation_str
        }
