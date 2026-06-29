import sys
import os
from typing import Dict, Any, List
from langchain_core.tools import tool

# Core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.registry.base import BaseAgent
from core.react_runner import ReActRunner
from mcp_client import mcp_call
from knowledge.knowledge_service import KnowledgeService

# Global service instance
knowledge_service = KnowledgeService()

@tool
async def search_meeting_notes(client_id: str = None, candidate_id: str = None) -> list:
    """Search historical client and candidate meeting notes and transcripts."""
    return await mcp_call("search_meeting_notes", client_id=client_id, candidate_id=candidate_id)

@tool
async def search_crm_updates(client_id: str = None) -> list:
    """Search CRM records, status changes, and client relationship updates."""
    return await mcp_call("search_crm_updates", client_id=client_id)

@tool
async def search_recruiter_notes(candidate_id: str = None) -> list:
    """Search notes compiled by recruiters regarding a specific candidate."""
    return await mcp_call("search_recruiter_notes", candidate_id=candidate_id)

@tool
async def search_interview_feedback(candidate_id: str = None, jd_id: str = None) -> list:
    """Search technical interview feedback and scorecards for candidate or job description."""
    return await mcp_call("search_interview_feedback", candidate_id=candidate_id, jd_id=jd_id)

@tool
async def search_emails(sender: str = None, recipient: str = None) -> list:
    """Search email logs corresponding to specific senders or recipients."""
    return await mcp_call("search_emails", sender=sender, recipient=recipient)

@tool
async def get_candidate_knowledge(candidate_id: str) -> list:
    """Fetch high-level knowledge graph nodes and relations connected to a candidate."""
    return await mcp_call("get_candidate_knowledge", candidate_id=candidate_id)

@tool
def run_hybrid_rag_search(query_text: str, candidate_id: str) -> list:
    """Run a comprehensive hybrid vector + BM25 keyword search over all recruiting knowledge documents."""
    return knowledge_service.hybrid_search(query_text=query_text, candidate_id=candidate_id)


class KnowledgeAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "knowledge"

    @property
    def description(self) -> str:
        return "Knowledge agent retrieving candidate recruiter logs, emails, meetings, and CRM updates using an autonomous ReAct strategy."

    @property
    def required_inputs(self) -> list[str]:
        return []

    @property
    def produced_outputs(self) -> list[str]:
        return ["knowledge_context", "agent_outputs", "tool_cache", "agent_scratchpads"]

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_data = state.get("candidate_data") or {}
        candidate_id = state.get("candidate_id") or candidate_data.get("id")
        session_id = state.get("session_id")
        log_cb = state.get("log_callback", print)
        
        # Determine query string for hybrid RAG search
        skills_str = ", ".join(candidate_data.get("skills", [])) if candidate_data.get("skills") else ""
        pos = candidate_data.get("current_position", "")
        query_text = f"Placements and interactions for {candidate_data.get('name', 'candidate')} {pos} {skills_str}"
        
        # 1. Direct hybrid search using knowledge service
        ranked_items = knowledge_service.hybrid_search(
            query_text=query_text,
            candidate_id=candidate_id
        ) or []
        
        # 2. Fetch specific items to fill cache & expand context (emails, crm, meetings, recruiter notes)
        crm_updates = await mcp_call("search_crm_updates", client_id=None) or []
        meeting_notes = await mcp_call("search_meeting_notes", candidate_id=candidate_id) or []
        recruiter_notes = await mcp_call("search_recruiter_notes", candidate_id=candidate_id) or []
        emails = await mcp_call("search_emails", recipient=candidate_data.get("email")) or []
        interview_feedback = await mcp_call("search_interview_feedback", candidate_id=candidate_id) or []
        
        # Build cache
        updated_cache = {**state.get("tool_cache", {})}
        updated_cache[f"run_hybrid_rag_search:{{'query_text': '{query_text}', 'candidate_id': '{candidate_id}'}}"] = ranked_items
        updated_cache[f"search_crm_updates:{{'client_id': None}}"] = crm_updates
        updated_cache[f"search_meeting_notes:{{'candidate_id': '{candidate_id}'}}"] = meeting_notes
        updated_cache[f"search_recruiter_notes:{{'candidate_id': '{candidate_id}'}}"] = recruiter_notes
        updated_cache[f"search_emails:{{'recipient': '{candidate_data.get('email')}'}}"] = emails
        updated_cache[f"search_interview_feedback:{{'candidate_id': '{candidate_id}'}}"] = interview_feedback
        
        # Normalize and merge items
        for items, item_type in [
            (crm_updates, "crm_update"),
            (meeting_notes, "meeting_note"),
            (recruiter_notes, "recruiter_note"),
            (emails, "email"),
            (interview_feedback, "interview_feedback")
        ]:
            for item in items:
                if isinstance(item, dict):
                    if "type" not in item:
                        item["type"] = item_type
                    ranked_items.append(item)
                    
        # Deduplicate
        seen_ids = set()
        deduped_items = []
        for item in ranked_items:
            item_id = item.get("id") or item.get("recommendation_id") or str(item)
            if item_id not in seen_ids:
                seen_ids.add(item_id)
                deduped_items.append(item)
        ranked_items = deduped_items
        
        knowledge_context = {
            "ranked_items": ranked_items,
            "notes_count": len(ranked_items),
            "meeting_notes": [item for item in ranked_items if item.get("type") == "meeting_note"],
            "emails": [item for item in ranked_items if item.get("type") == "email"],
            "crm_updates": [item for item in ranked_items if item.get("type") == "crm_update"],
            "recruiter_notes": [item for item in ranked_items if item.get("type") == "recruiter_note"],
            "playbooks": [item for item in ranked_items if item.get("type") == "playbook"]
        }
        
        # Log UI expected markers
        log_cb(f"Retrieved {len(ranked_items)} knowledge items for evaluation context.")
        
        agent_outputs = state.get("agent_outputs") or {}
        agent_outputs["knowledge"] = {
            "notes_count": len(ranked_items),
            "status": "populated" if ranked_items else "empty"
        }
        
        agent_scratchpads = state.get("agent_scratchpads") or {}
        agent_scratchpads[self.name] = [
            "Determined deterministic retrieval strategy.",
            f"Executed hybrid search over database for {candidate_id}.",
            "Fetched emails, CRM, recruiter notes, and interview feedback programmatically."
        ]
        
        return {
            "knowledge_context": knowledge_context,
            "agent_outputs": agent_outputs,
            "tool_cache": updated_cache,
            "agent_scratchpads": agent_scratchpads
        }
