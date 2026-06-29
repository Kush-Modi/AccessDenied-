import pytest
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.filters import load_ranking_config, filter_by_metadata, filter_by_similarity
from embeddings.embedder import embedder
from embeddings.indexing import run_indexing
from retrieval.metrics import RetrievalMetrics
from retrieval.ranking import rank_items
from retrieval.reranker import rerank_items
from explainability.scoring import DecisionScorer
from explainability.formatter import ExplainabilityFormatter
from knowledge.knowledge_service import KnowledgeService
from supabase_client import supabase

def test_config_loading():
    """Verify that configuration weights are loaded properly from ranking_config.yaml."""
    config = load_ranking_config()
    assert "weights" in config, "weights block missing from config"
    assert "retrieval" in config, "retrieval block missing from config"
    
    weights = config["weights"]
    assert weights.get("semantic_similarity") == 0.40
    assert weights.get("business_signals") == 0.20
    assert weights.get("client_health") == 0.15
    assert weights.get("placement_history") == 0.10
    
    ret = config["retrieval"]
    assert ret.get("top_k") == 5
    assert ret.get("similarity_threshold") == 0.75

def test_embedding_generation_and_caching():
    """Verify that sentence-transformers computes embeddings and stores in Redis."""
    text = "Machine Learning Engineer with NLP expertise"
    
    # 1. Fetch embedding (first time - cache miss)
    vector = embedder.get_embedding(text)
    assert isinstance(vector, list)
    assert len(vector) == 384
    assert all(isinstance(val, float) for val in vector)
    
    # 2. Fetch embedding again (second time - cache hit)
    vector2 = embedder.get_embedding(text)
    assert vector == vector2

def test_metrics_collection():
    """Verify metrics can be recorded and read back from Redis."""
    # Reset metrics first
    RetrievalMetrics.reset_metrics()
    
    RetrievalMetrics.record_latencies(0.05, 0.12, 0.01)
    RetrievalMetrics.record_counts(42, 8, 5)
    RetrievalMetrics.record_averages(0.82, 0.78)
    
    metrics = RetrievalMetrics.get_metrics()
    assert metrics["last_embedding_latency"] == 0.05
    assert metrics["last_retrieval_latency"] == 0.12
    assert metrics["last_rerank_latency"] == 0.01
    assert metrics["last_retrieved_count"] == 42
    assert metrics["last_filtered_count"] == 8
    assert metrics["last_reranked_count"] == 5
    assert metrics["last_average_similarity"] == 0.82
    assert metrics["last_average_confidence"] == 0.78
    assert metrics["total_queries"] >= 1

def test_ranking_and_reranking_logic():
    """Verify multi-signal ranking weights and keyword overlap reranker pass."""
    sample_items = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "type": "email",
            "title": "Discussion about Python developer position",
            "summary": "Urgent hire needed for Python expert",
            "content": "Client wants to sign-off and send offer to Python engineer.",
            "similarity": 0.85,
            "created_at": "2026-06-25T12:00:00Z",
            "metadata": {"importance": "high"}
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "type": "meeting_note",
            "title": "Weekly catchup",
            "summary": "Standard sync meeting.",
            "content": "Talked about weather and minor tasks.",
            "similarity": 0.78,
            "created_at": "2026-06-01T12:00:00Z",
            "metadata": {"importance": "low"}
        }
    ]
    
    # Run multi-signal scoring
    ranked = rank_items(sample_items)
    
    # First item should have higher final score due to similarity, business signal (urgent), and recency
    assert len(ranked) == 2
    assert ranked[0]["id"] == "11111111-1111-1111-1111-111111111111"
    assert ranked[0]["scores"]["final_score"] > ranked[1]["scores"]["final_score"]
    
    # Test keyword boost reranker
    reranked = rerank_items(ranked, query_text="Python offer")
    assert reranked[0]["scores"].get("lexical_boost", 0.0) > 0.0
    assert reranked[1]["scores"].get("lexical_boost", 0.0) == 0.0

def test_decision_scorer_and_explainability():
    """Verify that combined confidence and Evidence Tree are structured correctly."""
    service = KnowledgeService()
    
    # Retrieve some sample database items to score
    items = service.hybrid_search(
        query_text="developer",
        custom_top_k=2
    )
    
    # Calculate decision match
    result = DecisionScorer.calculate_decision(
        candidate_fit_score=0.85,
        ranked_knowledge_items=items,
        candidate_name="John Doe",
        client_name="Acme Corp",
        jd_title="Senior Python Developer"
    )
    
    assert "final_confidence" in result
    assert "evidence_tree" in result
    
    tree = result["evidence_tree"]
    assert tree["type"] == "Recommendation"
    assert tree["score"] > 0.0
    assert len(tree["children"]) == 4
    assert tree["children"][0]["type"] == "Evidence" # Capability
    assert tree["children"][1]["type"] == "Evidence" # Enterprise Knowledge

    
    # Format trace
    explanation = ExplainabilityFormatter.format_explanation(result, items)
    assert "markdown_explanation" in explanation
    assert "knowledge_trace" in explanation
    
    trace = explanation["knowledge_trace"]
    # Check that trace has type and ID
    for item in trace:
        assert "_" in item
        
    print("\nGenerated Markdown Explainability Tree:\n", explanation["markdown_explanation"])

def test_incremental_indexing():
    """Verify that running the indexer when fully synced does not throw errors."""
    count = run_indexing()
    # Should complete successfully and return 0 (since all 63 items are already indexed)
    assert isinstance(count, int)
    assert count == 0
