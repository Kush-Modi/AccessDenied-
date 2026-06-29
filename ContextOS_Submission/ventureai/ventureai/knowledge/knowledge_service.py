from typing import List, Dict, Any, Optional
import time
from knowledge.repository import KnowledgeRepository
from knowledge.knowledge_models import (
    KnowledgeItem,
    RecruiterNote,
    MeetingNote,
    Email,
    CRMUpdate,
    InterviewFeedback,
    CustomerInteraction
)
from embeddings.embedder import embedder
from retrieval.filters import filter_by_metadata, filter_by_similarity, load_ranking_config
from retrieval.ranking import rank_items
from retrieval.reranker import rerank_items
from retrieval.metrics import RetrievalMetrics


class KnowledgeService:
    """
    Service layer coordinating repository access and returning Pydantic models.
    """
    def __init__(self):
        self.repository = KnowledgeRepository()

    def get_knowledge_items(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        item_type: Optional[str] = None
    ) -> List[KnowledgeItem]:
        raw_items = self.repository.get_knowledge_items(entity_type, entity_id, item_type)
        return [KnowledgeItem(**item) for item in raw_items]

    def get_recruiter_notes(self, candidate_id: Optional[str] = None) -> List[RecruiterNote]:
        raw_notes = self.repository.get_recruiter_notes(candidate_id)
        return [RecruiterNote(**item) for item in raw_notes]

    def get_meeting_notes(
        self,
        client_id: Optional[str] = None,
        candidate_id: Optional[str] = None
    ) -> List[MeetingNote]:
        raw_meetings = self.repository.get_meeting_notes(client_id, candidate_id)
        return [MeetingNote(**item) for item in raw_meetings]

    def get_emails(
        self,
        sender: Optional[str] = None,
        recipient: Optional[str] = None
    ) -> List[Email]:
        raw_emails = self.repository.get_emails(sender, recipient)
        return [Email(**item) for item in raw_emails]

    def get_crm_updates(self, client_id: Optional[str] = None) -> List[CRMUpdate]:
        raw_crm = self.repository.get_crm_updates(client_id)
        return [CRMUpdate(**item) for item in raw_crm]

    def get_interview_feedback(
        self,
        candidate_id: Optional[str] = None,
        jd_id: Optional[str] = None
    ) -> List[InterviewFeedback]:
        raw_fb = self.repository.get_interview_feedback(candidate_id, jd_id)
        return [InterviewFeedback(**item) for item in raw_fb]

    def get_customer_interactions(
        self,
        client_id: Optional[str] = None,
        candidate_id: Optional[str] = None
    ) -> List[CustomerInteraction]:
        raw_ci = self.repository.get_customer_interactions(client_id, candidate_id)
        return [CustomerInteraction(**item) for item in raw_ci]

    def get_candidate_knowledge_context(self, candidate_id: str) -> Dict[str, Any]:
        """
        Return the structured context object for KnowledgeAgent.
        """
        meeting_notes = self.get_meeting_notes(candidate_id=candidate_id)
        recruiter_notes = self.get_recruiter_notes(candidate_id=candidate_id)
        
        # Emails can be linked by candidate name or candidate_id inside content,
        # but in our deterministic generation, they are mapped in knowledge_items.
        # Let's query knowledge_items for this candidate to find emails and crm updates too!
        items = self.get_knowledge_items(entity_type="candidate", entity_id=candidate_id)
        
        emails_list = [item.dict() for item in items if item.type == "email"]
        crm_list = [item.dict() for item in items if item.type == "crm"]
        playbooks_list = [item.dict() for item in items if item.type == "playbook"]
        
        # Add client-linked meeting notes or CRM logs if applicable
        # Let's also include standard parsed items
        return {
            "meeting_notes": [m.dict() for m in meeting_notes],
            "emails": emails_list,
            "crm_updates": crm_list,
            "playbooks": playbooks_list,
            "recruiter_notes": [r.dict() for r in recruiter_notes]
        }

    def hybrid_search(
        self,
        query_text: str,
        candidate_id: str = None,
        client_id: str = None,
        custom_threshold: float = None,
        custom_top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Execute Hybrid Search on knowledge_items:
        Semantic Embeddings -> Metadata Filtering -> Multi-Signal Decision Scoring -> Lexical Reranking -> Top K
        """
        # Load configuration
        config = load_ranking_config()
        threshold = custom_threshold if custom_threshold is not None else config.get("retrieval", {}).get("similarity_threshold", 0.75)
        top_k = custom_top_k if custom_top_k is not None else config.get("retrieval", {}).get("top_k", 5)

        # 1. Embed query
        start_embed = time.time()
        query_emb = embedder.get_embedding(query_text)
        embed_lat = time.time() - start_embed

        # 2. Vector search query
        start_retrieve = time.time()
        # Fetch up to 100 matching items to perform filtering in Python
        raw_items = self.repository.match_knowledge_items(
            query_embedding=query_emb,
            match_threshold=0.0, # Fetch all similarities so we can filter/decide in python
            match_count=100
        )
        retrieve_lat = time.time() - start_retrieve

        # Record counts
        retrieved_count = len(raw_items)

        # 3. Apply metadata filters
        filtered_items = filter_by_metadata(raw_items, candidate_id=candidate_id, client_id=client_id)
        
        # 4. Apply similarity threshold
        filtered_items = filter_by_similarity(filtered_items, custom_threshold=threshold)
        filtered_count = len(filtered_items)

        # 5. Apply multi-signal Decision Scorer ranking
        start_rerank = time.time()
        ranked_items = rank_items(filtered_items)

        # 6. Apply secondary lexical overlap reranker
        reranked_items = rerank_items(ranked_items, query_text=query_text)
        rerank_lat = time.time() - start_rerank

        # Slice to Top K
        top_k_items = reranked_items[:top_k]
        reranked_count = len(top_k_items)

        # 7. Record retrieval metrics
        RetrievalMetrics.record_latencies(embed_lat, retrieve_lat, rerank_lat)
        RetrievalMetrics.record_counts(retrieved_count, filtered_count, reranked_count)
        
        if top_k_items:
            avg_sim = sum(item.get("similarity", 0.0) for item in top_k_items) / len(top_k_items)
            avg_conf = sum(item.get("scores", {}).get("final_score", 0.0) for item in top_k_items) / len(top_k_items)
            RetrievalMetrics.record_averages(avg_sim, avg_conf)

        return top_k_items

