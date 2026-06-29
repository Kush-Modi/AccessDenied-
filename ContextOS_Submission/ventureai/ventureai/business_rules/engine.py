from typing import Dict, Any, List
from business_rules.loader import RuleLoader
from business_rules.evaluator import RuleEvaluator
from business_rules.models import Rule, RuleExecutionResult

class BusinessRulesEngine:
    def __init__(self, rules_file: str = None):
        self.rules = RuleLoader.load_rules(rules_file)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes all enabled business rules against the provided context.
        Returns evaluation metrics, net score adjustment, blocked state, and traces.
        """
        applied_results: List[RuleExecutionResult] = []
        blocked_results: List[RuleExecutionResult] = []
        rule_trace: List[Dict[str, Any]] = []
        
        score_adjustment = 0.0
        blocked = False
        suppressed = False
        escalated = False
        priority_override = None
        
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            is_match = RuleEvaluator.evaluate(rule.condition, context)
            
            # Map action adjustments
            adjustment = 0.0
            explanation = "Condition not met"
            
            if is_match:
                explanation = f"Condition matched: {rule.description}"
                if rule.action == "increase_confidence":
                    adjustment = rule.weight
                    score_adjustment += adjustment
                elif rule.action == "decrease_confidence":
                    adjustment = -rule.weight
                    score_adjustment += adjustment
                elif rule.action == "block":
                    blocked = True
                    adjustment = -1.0
                elif rule.action == "suppress":
                    suppressed = True
                    adjustment = -1.0
                elif rule.action == "escalate":
                    escalated = True
                elif rule.action == "override_priority":
                    priority_override = "Critical"
                    
                exec_res = RuleExecutionResult(
                    rule_id=rule.id,
                    name=rule.name,
                    description=rule.description,
                    action=rule.action,
                    weight=rule.weight,
                    applied=True,
                    explanation=explanation,
                    score_adjustment=adjustment
                )
                
                if rule.action in ["block", "suppress"]:
                    blocked_results.append(exec_res)
                else:
                    applied_results.append(exec_res)
            
            rule_trace.append({
                "rule_id": rule.id,
                "name": rule.name,
                "condition": rule.condition,
                "matched": is_match,
                "action": rule.action,
                "adjustment": adjustment
            })
            
        # Build explanation string
        lines = []
        if blocked:
            lines.append("Recommendation BLOCKED by business rules.")
        if suppressed:
            lines.append("Recommendation SUPPRESSED by business rules.")
        if escalated:
            lines.append("Escalation required for this recommendation.")
            
        for app in applied_results:
            op = "+" if app.score_adjustment > 0 else ""
            lines.append(f"- {app.name}: {op}{app.score_adjustment:.2f} ({app.description})")
            
        for blk in blocked_results:
            lines.append(f"- {blk.name}: BLOCKED/SUPPRESSED ({blk.description})")
            
        rule_explanation = "\n".join(lines) if lines else "No business rules triggered score adjustments."
        
        return {
            "applied_rules": [r.dict() for r in applied_results],
            "blocked_rules": [r.dict() for r in blocked_results],
            "rule_trace": rule_trace,
            "score_adjustment": score_adjustment,
            "blocked": blocked,
            "suppressed": suppressed,
            "escalated": escalated,
            "priority_override": priority_override,
            "explanation": rule_explanation
        }
