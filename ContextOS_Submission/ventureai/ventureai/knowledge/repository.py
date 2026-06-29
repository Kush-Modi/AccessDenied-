from typing import List, Dict, Any, Optional
from supabase_client import supabase

class KnowledgeRepository:
    """
    Direct data access class interacting with Supabase tables.
    Does not contain business logic.
    """
    
    def get_knowledge_items(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = supabase.table("knowledge_items").select("*")
        if entity_type:
            query = query.eq("entity_type", entity_type)
        if entity_id:
            query = query.eq("entity_id", entity_id)
        if item_type:
            query = query.eq("type", item_type)
        result = query.execute()
        return result.data or []

    def get_recruiter_notes(self, candidate_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = supabase.table("recruiter_notes").select("*")
        if candidate_id:
            query = query.eq("candidate_id", candidate_id)
        result = query.execute()
        return result.data or []

    def get_meeting_notes(
        self,
        client_id: Optional[str] = None,
        candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = supabase.table("meeting_notes").select("*")
        if client_id:
            query = query.eq("client_id", client_id)
        if candidate_id:
            query = query.eq("candidate_id", candidate_id)
        result = query.execute()
        return result.data or []

    def get_emails(
        self,
        sender: Optional[str] = None,
        recipient: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = supabase.table("emails").select("*")
        if sender:
            query = query.eq("sender", sender)
        if recipient:
            query = query.eq("recipient", recipient)
        result = query.execute()
        return result.data or []

    def get_crm_updates(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = supabase.table("crm_updates").select("*")
        if client_id:
            query = query.eq("client_id", client_id)
        result = query.execute()
        return result.data or []

    def get_interview_feedback(
        self,
        candidate_id: Optional[str] = None,
        jd_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = supabase.table("interview_feedback").select("*")
        if candidate_id:
            query = query.eq("candidate_id", candidate_id)
        if jd_id:
            query = query.eq("jd_id", jd_id)
        result = query.execute()
        return result.data or []

    def get_customer_interactions(
        self,
        client_id: Optional[str] = None,
        candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = supabase.table("customer_interactions").select("*")
        if client_id:
            query = query.eq("client_id", client_id)
        if candidate_id:
            query = query.eq("candidate_id", candidate_id)
        result = query.execute()
        return result.data or []

    def match_knowledge_items(
        self,
        query_embedding: List[float],
        match_threshold: float,
        match_count: int,
        filter_entity_type: Optional[str] = None,
        filter_entity_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count
        }
        if filter_entity_type:
            params["filter_entity_type"] = filter_entity_type
        if filter_entity_id:
            params["filter_entity_id"] = filter_entity_id
            
        result = supabase.rpc("match_knowledge_items", params).execute()
        return result.data or []

