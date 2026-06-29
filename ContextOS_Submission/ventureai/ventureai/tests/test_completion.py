import pytest
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_loader import ConfigLoader
from business_rules.evaluator import RuleEvaluator
from business_rules.engine import BusinessRulesEngine
from business_rules.loader import RuleLoader
from memory.repository import MemoryRepository
from memory.feedback_manager import FeedbackManager
from memory.learning import FeedbackLearner
from memory.planner_memory import PlannerMemory
from explainability.scoring import DecisionScorer
from explainability.formatter import ExplainabilityFormatter

def test_config_loader():
    """Verify config loading from ranking_config.yaml has correct defaults or overrides."""
    config = ConfigLoader.get_config()
    assert "cache" in config
    assert "retrieval" in config
    assert "decision_weights" in config
    
    weights = config["decision_weights"]
    assert weights.get("candidate_fit") == 0.35
    assert weights.get("knowledge_rag") == 0.25
    assert weights.get("planner_memory") == 0.20

def test_business_rules_evaluator():
    """Verify rule criteria match notice periods, salary/location mismatches, and health thresholds."""
    # 1. Salary Mismatch
    candidate = {"skills": ["Python"], "expected_salary": 4500000, "location": "Bangalore"}
    job = {"required_skills": ["Python"], "salary_range": "25-35 LPA", "location": "Bangalore"}
    client = {"account_health": 85}
    
    ctx = RuleEvaluator.build_context(candidate, client, job)
    assert ctx["salary_mismatch"] is True
    assert ctx["location_mismatch"] is False
    assert ctx["missing_mandatory_skills"] is False
    
    # 2. Location Mismatch
    candidate2 = {"skills": ["Python"], "location": "Mumbai"}
    job2 = {"required_skills": ["Python"], "location": "Bangalore"}
    ctx2 = RuleEvaluator.build_context(candidate2, client, job2)
    assert ctx2["location_mismatch"] is True
    
    # 3. Client Health threshold comparison
    assert RuleEvaluator.evaluate("client_health < 40", {"client_health": 30}) is True
    assert RuleEvaluator.evaluate("client_health < 40", {"client_health": 60}) is False

def test_business_rules_engine():
    """Verify that rules load and execute adjustments cleanly."""
    rules_engine = BusinessRulesEngine()
    assert len(rules_engine.rules) > 0
    
    # Trigger low client health and notice period rules
    context = {
        "client_health": 30, # Trigger client_health < 40
        "candidate_notice_period_long": True, # Trigger notice period long
        "hiring_freeze": False,
        "candidate_rejected_recently": False,
        "candidate_already_submitted": False,
        "candidate_unavailable": False,
        "urgent_hiring": False,
        "duplicate_recommendation": False,
        "salary_mismatch": False,
        "location_mismatch": False,
        "missing_mandatory_skills": False
    }
    
    res = rules_engine.run(context)
    assert res["score_adjustment"] < 0.0 # Net decrease
    assert res["blocked"] is False
    assert any(r["rule_id"] == "RULE_CLIENT_HEALTH_LOW" for r in res["applied_rules"])
    
    # Trigger block rule
    context["hiring_freeze"] = True
    res_blocked = rules_engine.run(context)
    assert res_blocked["blocked"] is True

def test_planner_memory_repository():
    """Verify database repository operations for logging decisions and outcomes."""
    # Log a dummy approval decision
    cand_id = "test_candidate_123"
    client_id = "test_client_abc"
    job_id = "test_job_xyz"
    rec_id = f"test_rec_{os.urandom(4).hex()}"
    
    rec = FeedbackManager.log_recruiter_decision(
        candidate_id=cand_id,
        client_id=client_id,
        job_id=job_id,
        decision="approved",
        recommendation_id=rec_id,
        reason="Excellent profile overlap",
        confidence=0.88
    )
    
    # Check that feedback is written to Supabase (or offline mock fallback)
    assert rec is not None
    
    # Log placement outcome success
    outcome_rec = FeedbackManager.log_placement_outcome(
        recommendation_id=rec_id,
        outcome="success",
        notes="Hired successfully by client"
    )
    
    assert outcome_rec is not None
    
    # Fetch historical context
    memory_ctx = PlannerMemory.get_memory_context(
        candidate_id=cand_id,
        client_id=client_id,
        job_id=job_id
    )
    
    assert memory_ctx["history_count"] >= 1
    assert memory_ctx["success_rate"] > 0.0 or memory_ctx["memory_score"] > 0.0

def test_decision_scorer_combined():
    """Verify combined score calculation and evidence tree builds correctly."""
    # Mock parameters
    fit = 0.90
    items = [{"id": "item1", "type": "meeting_note", "title": "Client sync", "scores": {"final_score": 0.80}}]
    
    rules_res = {
        "applied_rules": [{"name": "Urgent hiring boost", "action": "increase_confidence", "score_adjustment": 0.10, "description": "Urgent"}],
        "blocked_rules": [],
        "score_adjustment": 0.10,
        "blocked": False,
        "suppressed": False,
        "explanation": "Urgent hiring boost: +0.10"
    }
    
    memory_ctx = {
        "memory_score": 0.75,
        "learning_score": 0.10,
        "explanation": "Good success history",
        "history_count": 2,
        "history_trace": [{"recommendation_id": "r1", "decision": "approved", "outcome": "success", "timestamp": "2026-06-25"}]
    }
    
    res = DecisionScorer.calculate_decision(
        candidate_fit_score=fit,
        ranked_knowledge_items=items,
        candidate_name="Jane Dev",
        client_name="Innovate Corp",
        jd_title="Software Architect",
        business_rules_res=rules_res,
        memory_context=memory_ctx,
        client_health=0.85,
        priority_urgency_score=1.0
    )
    
    assert "final_confidence" in res
    assert res["final_confidence"] > 0.0
    assert "evidence_tree" in res
    assert res["business_rules"]["score_adjustment"] == 0.10
    
    tree = res["evidence_tree"]
    # Evidence tree should have 4 main branches (capability, knowledge, rules, memory)
    assert len(tree["children"]) == 4

def test_explainability_traces_json_serializable():
    """Verify that formatted trace dictionaries are clean and fully JSON serializable."""
    fit = 0.85
    items = [{"id": "item_abc", "type": "email", "title": "Job follow up", "scores": {"final_score": 0.70}}]
    
    decision = DecisionScorer.calculate_decision(
        candidate_fit_score=fit,
        ranked_knowledge_items=items,
        candidate_name="Alice Smith",
        client_name="NextGen Inc",
        jd_title="Frontend Lead"
    )
    
    planner_steps = ["Inception", "Analysis", "Validation", "Rules Checking", "Final Decision"]
    
    explanation = ExplainabilityFormatter.format_explanation(decision, items, planner_steps)
    
    # Assert trace exists in the output
    assert "knowledge_trace" in explanation
    assert "retrieval_trace" in explanation
    assert "planner_trace" in explanation
    assert "decision_trace" in explanation
    assert "business_rule_trace" in explanation
    assert "memory_trace" in explanation
    assert "confidence_breakdown" in explanation
    
    # Test JSON serialization to verify that there are no custom object types (like EvidenceNode) in traces
    try:
        serialized = json.dumps(explanation)
        loaded = json.loads(serialized)
        assert loaded["confidence_breakdown"]["candidate_fit_score"] == 0.85
    except Exception as e:
        pytest.fail(f"Explainability payload serialization failed: {e}")
