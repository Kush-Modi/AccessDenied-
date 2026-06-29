import os
import sys
from typing import List, Dict, Any, Optional
from explainability.evidence import EvidenceNode
from core.config_loader import ConfigLoader

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DecisionScorer:
    @staticmethod
    def calculate_decision(
        candidate_fit_score: float,
        ranked_knowledge_items: List[Dict[str, Any]],
        candidate_name: str,
        client_name: str,
        jd_title: str,
        business_rules_res: Optional[Dict[str, Any]] = None,
        memory_context: Optional[Dict[str, Any]] = None,
        client_health: float = 0.6,
        priority_urgency_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Combines Candidate Fit Score, Top RAG Knowledge, Planner Memory,
        Client Health, and Priority/Urgency using dynamic weights from ConfigLoader,
        plus Business Rules adjustments, to compute a deterministic final Decision
        Intelligence Confidence Score. Constructs and returns the hierarchical Evidence Tree.
        """
        # Load weights from config
        config = ConfigLoader.get_config()
        weights = config.get("decision_weights", {})
        
        w_cand = weights.get("candidate_fit", 0.35)
        w_rag = weights.get("knowledge_rag", 0.25)
        w_mem = weights.get("planner_memory", 0.20)
        w_health = weights.get("client_health", 0.10)
        w_priority = weights.get("priority_urgency", 0.10)

        # Determine top retrieved knowledge score
        top_knowledge_score = 0.5
        top_item = None
        if ranked_knowledge_items:
            top_item = ranked_knowledge_items[0]
            top_knowledge_score = top_item.get("scores", {}).get("final_score", 0.5)

        # Get memory components
        memory_score = 0.5
        memory_adj = 0.0
        memory_explanation = "No memory history loaded"
        history_count = 0
        if memory_context:
            memory_score = memory_context.get("memory_score", 0.5)
            memory_adj = memory_context.get("learning_score", 0.0)
            memory_explanation = memory_context.get("explanation", "")
            history_count = memory_context.get("history_count", 0)

        # Get business rules components
        rule_adj = 0.0
        blocked = False
        suppressed = False
        escalated = False
        rule_explanation = "No business rules executed"
        applied_rules = []
        blocked_rules = []
        if business_rules_res:
            rule_adj = business_rules_res.get("score_adjustment", 0.0)
            blocked = business_rules_res.get("blocked", False)
            suppressed = business_rules_res.get("suppressed", False)
            escalated = business_rules_res.get("escalated", False)
            rule_explanation = business_rules_res.get("explanation", "")
            applied_rules = business_rules_res.get("applied_rules", [])
            blocked_rules = business_rules_res.get("blocked_rules", [])

        # Deterministic Base Score using dynamic config weights
        base_score = (w_cand * candidate_fit_score) + \
                     (w_rag * top_knowledge_score) + \
                     (w_mem * memory_score) + \
                     (w_health * client_health) + \
                     (w_priority * priority_urgency_score)

        final_confidence = base_score + rule_adj
        final_confidence = max(0.0, min(1.0, final_confidence))

        if blocked or suppressed:
            final_confidence = 0.0

        # Build hierarchical Evidence Tree nodes
        rec_description = f"Recommend matching {candidate_name} for the position of {jd_title} at {client_name}."
        if blocked:
            rec_description += " [BLOCKED BY RULES]"
        elif suppressed:
            rec_description += " [SUPPRESSED BY RULES]"
            
        root_node = EvidenceNode(
            node_type="Recommendation",
            title="Match Recommendation",
            description=rec_description,
            score=final_confidence
        )

        # 1. Candidate Capability node
        cand_node = EvidenceNode(
            node_type="Evidence",
            title=f"Candidate Match Capability (Weight: {w_cand*100:.0f}%)",
            description=f"Skill profiling match for candidate {candidate_name} shows strong alignment.",
            score=candidate_fit_score
        )
        root_node.children.append(cand_node)

        # 2. Enterprise Knowledge node
        knowledge_node = EvidenceNode(
            node_type="Evidence",
            title=f"Enterprise Knowledge Signal (Weight: {w_rag*100:.0f}%)",
            description=f"Historical interactions with client {client_name} and candidate {candidate_name} context.",
            score=top_knowledge_score
        )
        root_node.children.append(knowledge_node)

        # Add child nodes to Enterprise Knowledge based on retrieved items
        for idx, item in enumerate(ranked_knowledge_items[:3]): # Top 3 items
            scores = item.get("scores", {})
            itype = item.get("type", "Interaction")
            node_type = "Interaction"
            if "note" in itype.lower():
                node_type = "Meeting Note" if "meeting" in itype.lower() else "Recruiter Note"
            elif "email" in itype.lower():
                node_type = "Email"
            elif "crm" in itype.lower():
                node_type = "CRM Update"
            elif "feedback" in itype.lower():
                node_type = "Interview Feedback"
                
            item_node = EvidenceNode(
                node_type=node_type,
                title=f"Source Document: {item.get('title') or itype}",
                description=f"Summary: {item.get('summary') or 'No summary'}",
                score=scores.get("final_score", 0.5),
                source_id=item.get("id")
            )
            knowledge_node.children.append(item_node)

        # 3. Business Rules Engine node
        rules_node = EvidenceNode(
            node_type="Evidence",
            title="Business Rules Engine (Adjustments)",
            description=rule_explanation,
            score=0.5 + (rule_adj / 2.0)
        )
        root_node.children.append(rules_node)
        
        # Add child nodes for applied/blocked rules
        for r in applied_rules + blocked_rules:
            r_node = EvidenceNode(
                node_type="Rule",
                title=f"Triggered Rule: {r.get('name')}",
                description=f"Action: {r.get('action')} | {r.get('description')}",
                score=r.get("score_adjustment", 0.0)
            )
            rules_node.children.append(r_node)

        # 4. Planner Memory node
        memory_node = EvidenceNode(
            node_type="Evidence",
            title=f"Planner Memory (Weight: {w_mem*100:.0f}%)",
            description=f"Analyzed {history_count} previous recruiter feedback log(s). {memory_explanation}",
            score=memory_score
        )
        root_node.children.append(memory_node)
        
        if memory_context and "history_trace" in memory_context:
            for hist in memory_context["history_trace"][:3]:
                h_node = EvidenceNode(
                    node_type="MemoryTrace",
                    title=f"Previous Recruiter Decision: {hist.get('decision')}",
                    description=f"Outcome: {hist.get('outcome')} at {hist.get('timestamp')}",
                    score=1.0 if hist.get("decision") == "approved" else 0.0
                )
                memory_node.children.append(h_node)

        score_breakdown = {
            "candidate_fit_score": candidate_fit_score,
            "top_knowledge_score": top_knowledge_score,
            "memory_score": memory_score,
            "client_health": client_health,
            "priority_urgency_score": priority_urgency_score,
            "rule_adjustment": rule_adj,
            "base_score": base_score
        }

        return {
            "final_confidence": final_confidence,
            "score_breakdown": score_breakdown,
            "blocked": blocked,
            "suppressed": suppressed,
            "escalated": escalated,
            "evidence_tree": root_node.to_dict(),
            "business_rules": {
                "applied_rules": applied_rules,
                "blocked_rules": blocked_rules,
                "score_adjustment": rule_adj,
                "explanation": rule_explanation
            },
            "planner_memory": {
                "memory_score": memory_score,
                "learning_score": memory_adj,
                "explanation": memory_explanation,
                "history_count": history_count
            }
        }
