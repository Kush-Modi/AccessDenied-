from typing import List, Dict, Any

class ExplainabilityFormatter:
    @staticmethod
    def generate_knowledge_trace(ranked_items: List[Dict[str, Any]]) -> List[str]:
        """
        Generate the trace array mapping to IDs / names of the source documents referenced.
        e.g., ["meeting_note_23", "crm_update_11"]
        """
        trace = []
        for idx, item in enumerate(ranked_items):
            itype = item.get("type", "interaction").lower().replace(" ", "_")
            iid = item.get("id")
            short_id = str(iid)[:8] if iid else str(idx)
            trace.append(f"{itype}_{short_id}")
        return trace

    @staticmethod
    def _render_tree_node(node: Dict[str, Any], indent: int = 0) -> str:
        """Helper to recursively draw the tree structure in markdown."""
        prefix = "  " * indent + "+-- " if indent > 0 else ""

        lines = [f"{prefix}**{node['type']}**: {node['title']} (Score: {node['score'] * 100:.1f}%)"]
        if node.get("description"):
            lines.append("  " * (indent + 1) + f"_Description: {node['description']}_")
        if node.get("source_id"):
            lines.append("  " * (indent + 1) + f"_Source Reference: {node['source_id']}_")
            
        for child in node.get("children", []):
            lines.append(ExplainabilityFormatter._render_tree_node(child, indent + 1))
        return "\n".join(lines)

    @classmethod
    def format_explanation(
        cls,
        decision_payload: Dict[str, Any],
        ranked_items: List[Dict[str, Any]],
        planner_steps: List[str] = None
    ) -> Dict[str, Any]:
        """
        Formats evidence tree into readable markdown and extracts all requested traces (JSON serializable).
        """
        tree = decision_payload.get("evidence_tree", {})
        markdown_tree = cls._render_tree_node(tree)
        
        # 1. Knowledge Trace (Top references)
        k_trace = cls.generate_knowledge_trace(ranked_items)
        
        # 2. Retrieval Trace (Full list of retrieved IDs)
        r_trace = [str(item.get("id")) for item in ranked_items if item.get("id")]
        
        # 3. Planner Trace
        p_trace = planner_steps or ["Task Planning initiated", "Specialist agents invoked", "Decision compiled"]
        
        # 4. Decision Trace (Breakdown parameters)
        breakdown = decision_payload.get("score_breakdown", {})
        d_trace = [
            f"Candidate Match Score (35% weight): {breakdown.get('candidate_fit_score', 0.5):.2f}",
            f"Enterprise Knowledge Score (25% weight): {breakdown.get('top_knowledge_score', 0.5):.2f}",
            f"Planner Memory Score (20% weight): {breakdown.get('memory_score', 0.5):.2f}",
            f"Client Health Score (10% weight): {breakdown.get('client_health', 0.6):.2f}",
            f"Priority/Urgency Score (10% weight): {breakdown.get('priority_urgency_score', 0.5):.2f}",
            f"Business Rule Adjustments: {breakdown.get('rule_adjustment', 0.0):.2f}",
            f"Base Score before rules: {breakdown.get('base_score', 0.5):.2f}"
        ]
        
        # 5. Business Rule Trace
        rules_info = decision_payload.get("business_rules", {})
        br_trace = []
        for r in rules_info.get("applied_rules", []):
            br_trace.append(f"Applied Rule '{r.get('name')}': {r.get('score_adjustment', 0.0):+.2f} adjustment ({r.get('description')})")
        for r in rules_info.get("blocked_rules", []):
            br_trace.append(f"Blocking Rule '{r.get('name')}' TRIGGERED: Action {r.get('action')} ({r.get('description')})")
            
        # 6. Memory Trace
        mem_info = decision_payload.get("planner_memory", {})
        m_trace = [
            f"Memory Score: {mem_info.get('memory_score', 0.5):.2f}",
            f"Learning Score adjustment: {mem_info.get('learning_score', 0.0):+.2f}",
            f"Explanation: {mem_info.get('explanation', '')}",
            f"Total history count checked: {mem_info.get('history_count', 0)}"
        ]

        markdown_explanation = (
            f"### Decision Confidence: {decision_payload['final_confidence'] * 100:.1f}%\n\n"
            f"#### Hierarchical Evidence Tree:\n"
            f"```text\n"
            f"{markdown_tree}\n"
            f"```\n\n"
            f"#### Knowledge Trace:\n"
            f"The matching decision was derived from the following enterprise logs:\n"
            + "\n".join([f"- **{t}**" for t in k_trace])
            + f"\n\n#### Business Rules Applied:\n"
            + (rules_info.get("explanation") or "No business rules applied.")
            + f"\n\n#### Planner Memory & Feedback:\n"
            + (mem_info.get("explanation") or "No prior history found.")
        )

        return {
            "markdown_explanation": markdown_explanation,
            "knowledge_trace": k_trace,
            "retrieval_trace": r_trace,
            "planner_trace": p_trace,
            "decision_trace": d_trace,
            "business_rule_trace": br_trace,
            "memory_trace": m_trace,
            "confidence_breakdown": breakdown,
            "evidence_tree": tree,
            "reasoning_summary": markdown_tree.split("\n")[0] if markdown_tree else "Match Recommendation"
        }

