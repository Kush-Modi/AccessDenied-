import os
import json
import time
from typing import TypedDict, Annotated, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage

from mcp_client import mcp_call
from redis_client import set_hitl_pending, cache_set, log_session
from supabase_client import supabase

# Core Platform Imports
from core.registry.registry import AgentRegistry
from core.execution.context import ExecutionContext
from agents.planner.planner_agent import PlannerAgent
from agents.candidate.candidate_agent import CandidateAgent
from agents.client.client_agent import ClientAgent
from agents.knowledge.knowledge_agent import KnowledgeAgent
from agents.action.action_planner_agent import ActionPlannerAgent

# Register the specialist agents
AgentRegistry.register(PlannerAgent())
AgentRegistry.register(CandidateAgent())
AgentRegistry.register(ClientAgent())
AgentRegistry.register(KnowledgeAgent())
AgentRegistry.register(ActionPlannerAgent())

def log_event(session_id: str, message: str):
    print(message)
    if session_id:
        log_session(session_id, message)

from core.llm_client import llm, MatchRecommendation, safe_ainvoke, get_structured_llm

def merge_dicts(left: dict, right: dict) -> dict:
    if left is None:
        left = {}
    if right is None:
        right = {}
    return {**left, **right}

def merge_scratchpads(left: dict, right: dict) -> dict:
    if left is None:
        left = {}
    if right is None:
        right = {}
    res = {**left}
    for k, v in right.items():
        if k in res:
            res[k] = list(res[k]) + list(v)
        else:
            res[k] = v
    return res

def merge_execution_contexts(left: Any, right: Any) -> Any:
    if left is None:
        return right
    if right is None:
        return left
    
    # Handle dict/object representation
    left_completed = left.get("completed_agents") if isinstance(left, dict) else getattr(left, "completed_agents", [])
    right_completed = right.get("completed_agents") if isinstance(right, dict) else getattr(right, "completed_agents", [])
    completed = list(set((left_completed or []) + (right_completed or [])))
    
    left_timing = left.get("execution_timing") if isinstance(left, dict) else getattr(left, "execution_timing", {})
    right_timing = right.get("execution_timing") if isinstance(right, dict) else getattr(right, "execution_timing", {})
    timing = {**(left_timing or {}), **(right_timing or {})}
    
    left_history = left.get("execution_history") if isinstance(left, dict) else getattr(left, "execution_history", [])
    right_history = right.get("execution_history") if isinstance(right, dict) else getattr(right, "execution_history", [])
    history = list(left_history or []) + list(right_history or [])
    
    left_errors = left.get("errors") if isinstance(left, dict) else getattr(left, "errors", [])
    right_errors = right.get("errors") if isinstance(right, dict) else getattr(right, "errors", [])
    errors = list(left_errors or []) + list(right_errors or [])
    
    current_agent = right.get("current_agent") if isinstance(right, dict) else getattr(right, "current_agent", None)
    
    return {
        "current_agent": current_agent or (left.get("current_agent") if isinstance(left, dict) else getattr(left, "current_agent", None)),
        "completed_agents": completed,
        "execution_timing": timing,
        "execution_history": history,
        "errors": errors
    }

# Evolved Shared State Definition (Backward Compatible with TypedDict)
class AgentState(TypedDict):
    candidate_id: str
    messages: list
    candidate_data: dict
    matched_jobs: List[dict]
    top_recommendation: dict
    reasoning: str
    confidence: float
    hitl_status: str
    session_id: str
    
    # Evolved platform fields
    planner_tasks: List[Dict[str, Any]]
    completed_tasks: List[str]
    candidate_context: dict
    client_context: dict
    knowledge_context: dict
    execution_context: Annotated[Any, merge_execution_contexts]
    agent_outputs: Annotated[dict, merge_dicts]
    planner_reasoning: str
    knowledge_trace: list
    evidence_tree: dict
    retrieval_trace: list
    planner_trace: list
    decision_trace: list
    business_rule_trace: list
    memory_trace: list
    confidence_breakdown: dict
    
    # ReAct autonomous mode fields
    execution_mode: str
    agent_scratchpads: Annotated[Dict[str, List[str]], merge_scratchpads]
    tool_cache: Annotated[Dict[str, Any], merge_dicts]




# --- Langchain Proxy Tools (for LLM tool binding description - retained for backward compatibility / legacy code) ---
@tool
def get_candidate_profile(candidate_id: str) -> str:
    """Fetch the candidate profile by their unique ID, returning their name, email, skills, experience, current position, and resume."""
    pass

@tool
def search_job_descriptions(query_skills: str) -> str:
    """Search open job descriptions by matching comma-separated skill keywords. Returns a list of jobs."""
    pass

@tool
def get_placement_history(candidate_id: str = None, client_id: str = None) -> str:
    """Fetch the past placement and hire records for a specific candidate or client from the memory layer."""
    pass


# --- Helper to Update Execution Context ---
def update_execution_context(current_ctx: Any, agent_name: str, duration: float, error: str = None) -> Dict[str, Any]:
    # Ensure current_ctx is a dict or ExecutionContext
    if not current_ctx:
        completed = []
        timing = {}
        history = []
        errors = []
    elif hasattr(current_ctx, "model_copy"):
        completed = current_ctx.completed_agents or []
        timing = current_ctx.execution_timing or {}
        history = current_ctx.execution_history or []
        errors = current_ctx.errors or []
    else:
        completed = current_ctx.get("completed_agents") or []
        timing = current_ctx.get("execution_timing") or {}
        history = current_ctx.get("execution_history") or []
        errors = current_ctx.get("errors") or []
        
    completed = list(completed)
    if agent_name not in completed:
        completed.append(agent_name)
        
    timing = {**timing, agent_name: duration}
    history = list(history) + [{"agent": agent_name, "duration_seconds": duration, "status": "failed" if error else "success"}]
    
    if error:
        errors = list(errors) + [error]
        
    return {
        "current_agent": agent_name,
        "completed_agents": completed,
        "execution_timing": timing,
        "execution_history": history,
        "errors": errors
    }


# --- Refactored Platform V2 Graph Nodes ---

async def run_planner_node(state: AgentState):
    session_id = state.get("session_id")
    log_event(session_id, "\n>>> [PLANNER AGENT] Starting Graph Orchestration...")
    start_time = time.time()
    
    state_with_callback = {**state, "log_callback": lambda msg: log_event(session_id, msg)}
    planner = AgentRegistry.get("planner")
    res = await planner.execute(state_with_callback)
    
    duration = time.time() - start_time
    log_event(session_id, f"<<< [PLANNER AGENT] Plan compiled successfully in {duration:.3f}s.")
    log_event(session_id, f"    - Mode: {res.get('execution_mode', 'sequential').upper()}")
    log_event(session_id, f"    - Plan generated: {[t['agent'] for t in res.get('planner_tasks', [])]}")
    
    ctx_updates = update_execution_context(state.get("execution_context"), "planner", duration)
    
    return {
        "planner_tasks": res.get("planner_tasks"),
        "planner_reasoning": res.get("planner_reasoning"),
        "execution_mode": res.get("execution_mode"),
        "agent_scratchpads": res.get("agent_scratchpads"),
        "tool_cache": res.get("tool_cache"),
        "execution_context": ctx_updates
    }

async def run_candidate_node(state: AgentState):
    session_id = state.get("session_id")
    log_event(session_id, "\n>>> [CANDIDATE AGENT] Started execution...")
    start_time = time.time()
    
    state_with_callback = {**state, "log_callback": lambda msg: log_event(session_id, msg)}
    candidate_agent = AgentRegistry.get("candidate")
    res = await candidate_agent.execute(state_with_callback)
    
    duration = time.time() - start_time
    log_event(session_id, f"<<< [CANDIDATE AGENT] Completed in {duration:.3f}s.")
    
    ctx_updates = update_execution_context(state.get("execution_context"), "candidate", duration)
    
    return {
        "candidate_context": res.get("candidate_context"),
        "candidate_data": res.get("candidate_data"),
        "matched_jobs": res.get("matched_jobs"),
        "agent_outputs": res.get("agent_outputs"),
        "tool_cache": res.get("tool_cache"),
        "agent_scratchpads": res.get("agent_scratchpads"),
        "execution_context": ctx_updates
    }

async def run_client_node(state: AgentState):
    session_id = state.get("session_id")
    log_event(session_id, "\n>>> [CLIENT AGENT] Started execution...")
    start_time = time.time()
    
    state_with_callback = {**state, "log_callback": lambda msg: log_event(session_id, msg)}
    client_agent = AgentRegistry.get("client")
    res = await client_agent.execute(state_with_callback)
    
    duration = time.time() - start_time
    log_event(session_id, f"<<< [CLIENT AGENT] Completed in {duration:.3f}s.")
    
    ctx_updates = update_execution_context(state.get("execution_context"), "client", duration)
    
    return {
        "client_context": res.get("client_context"),
        "agent_outputs": res.get("agent_outputs"),
        "tool_cache": res.get("tool_cache"),
        "agent_scratchpads": res.get("agent_scratchpads"),
        "execution_context": ctx_updates
    }

async def run_knowledge_node(state: AgentState):
    session_id = state.get("session_id")
    log_event(session_id, "\n>>> [KNOWLEDGE AGENT] Started execution...")
    start_time = time.time()
    
    state_with_callback = {**state, "log_callback": lambda msg: log_event(session_id, msg)}
    knowledge_agent = AgentRegistry.get("knowledge")
    res = await knowledge_agent.execute(state_with_callback)
    
    duration = time.time() - start_time
    log_event(session_id, f"<<< [KNOWLEDGE AGENT] Completed in {duration:.3f}s.")
    
    ctx_updates = update_execution_context(state.get("execution_context"), "knowledge", duration)
    
    return {
        "knowledge_context": res.get("knowledge_context"),
        "agent_outputs": res.get("agent_outputs"),
        "tool_cache": res.get("tool_cache"),
        "agent_scratchpads": res.get("agent_scratchpads"),
        "execution_context": ctx_updates
    }

async def run_action_planner_node(state: AgentState):
    session_id = state.get("session_id")
    log_event(session_id, "\n>>> [ACTION PLANNER AGENT] Starting structured evaluation...")
    start_time = time.time()
    
    state_with_callback = {**state, "log_callback": lambda msg: log_event(session_id, msg)}
    action_agent = AgentRegistry.get("action")
    res = await action_agent.execute(state_with_callback)
    
    duration = time.time() - start_time
    log_event(session_id, f"<<< [ACTION PLANNER AGENT] Completed in {duration:.3f}s.")
    log_event(session_id, f"    - Final Recommendation: {res.get('top_recommendation', {}).get('job_title', 'None')} (Confidence: {res.get('confidence', 0.0)})")
    
    ctx_updates = update_execution_context(state.get("execution_context"), "action", duration)
    
    return {
        "top_recommendation": res.get("top_recommendation"),
        "reasoning": res.get("reasoning"),
        "confidence": res.get("confidence"),
        "knowledge_trace": res.get("knowledge_trace"),
        "retrieval_trace": res.get("retrieval_trace"),
        "planner_trace": res.get("planner_trace"),
        "decision_trace": res.get("decision_trace"),
        "business_rule_trace": res.get("business_rule_trace"),
        "memory_trace": res.get("memory_trace"),
        "evidence_tree": res.get("evidence_tree"),
        "confidence_breakdown": res.get("confidence_breakdown"),
        "agent_outputs": res.get("agent_outputs"),
        "tool_cache": res.get("tool_cache"),
        "agent_scratchpads": res.get("agent_scratchpads"),
        "execution_context": ctx_updates
    }

def hitl_gate(state: AgentState):
    """Node: HITL interrupt. Pauses execution until recruiter responds."""
    rec = state["top_recommendation"]
    session_id = state["session_id"]
    
    log_event(session_id, f"\n>>> [HITL APPROVAL GATE] Saving pending recommendation for {state['candidate_data'].get('name')} to Redis...")
    set_hitl_pending(session_id, {
        "candidate_id": state["candidate_id"],
        "candidate_name": state["candidate_data"].get("name"),
        "recommended_action": f"Pitch {state['candidate_data'].get('name')} to {rec.get('client_name')} for {rec.get('job_title')}",
        "reasoning": state["reasoning"],
        "confidence": state["confidence"],
        "job_id": rec.get("job_id"),
        "client_id": rec.get("client_id"),
    })
    
    log_event(session_id, "    !!! GRAPH PAUSED. Awaiting recruiter response (Approve/Reject)...")
    human_response = interrupt({
        "session_id": session_id,
        "message": f"Approve pitching {state['candidate_data'].get('name')} to {rec.get('client_name')}?",
        "reasoning": state["reasoning"],
        "confidence": state["confidence"],
    })
    
    log_event(session_id, f"    <<< GRAPH RESUMED. Recruiter decision received: {human_response.get('decision', 'rejected').upper()}")
    return {"hitl_status": human_response.get("decision", "rejected")}

async def execute_action(state: AgentState):
    """Node: Log recruiter action to Supabase and cache finalised Next Best Action."""
    decision = state["hitl_status"]
    session_id = state["session_id"]
    log_event(session_id, f"\n>>> [ACTION EXECUTION] Processing final decision: {decision}")
    
    rec = state["top_recommendation"]
    
    # Log the action (both approval and rejection) to Supabase so the system learns
    log_event(session_id, f"    - Logging recruiter action ({decision}) to Supabase 'recruiter_actions' table...")
    await mcp_call(
        "log_recruiter_action",
        action_type="pitch_candidate",
        target_id=state["candidate_id"],
        target_type="candidate",
        reason=state["reasoning"],
        recruiter_decision=decision,
    )
    
    # Log to planner memory feedback loop
    try:
        from memory.feedback_manager import FeedbackManager
        FeedbackManager.log_recruiter_decision(
            candidate_id=state["candidate_id"],
            client_id=rec.get("client_id"),
            job_id=rec.get("job_id"),
            decision=decision,
            recommendation_id=session_id,
            reason=state["reasoning"],
            confidence=state["confidence"]
        )
        log_event(session_id, "    - Successfully logged decision to Planner Memory table.")
    except Exception as e:
        log_event(session_id, f"    - Warning: Failed to log decision to Planner Memory: {e}")

    
    if decision == "approved":
        log_event(session_id, f"    - Caching finalized Next Best Action to Redis key: nba:{state['candidate_id']}")
        cache_set(f"nba:{state['candidate_id']}", {
            "candidate_id": state["candidate_id"],
            "candidate_name": state["candidate_data"].get("name"),
            "action": rec,
            "reasoning": state["reasoning"],
            "confidence": state["confidence"],
            "status": "approved",
            "session_id": state["session_id"],
        }, ttl=600)
    else:
        log_event(session_id, f"    - Action rejected. Caching rejection status to Redis key: nba:{state['candidate_id']}")
        cache_set(f"nba:{state['candidate_id']}", {
            "candidate_id": state["candidate_id"],
            "candidate_name": state["candidate_data"].get("name"),
            "action": rec,
            "reasoning": state["reasoning"],
            "confidence": state["confidence"],
            "status": "rejected",
            "session_id": state["session_id"],
        }, ttl=600)
        
    log_event(session_id, ">>> [WORKFLOW COMPLETED SUCCESSFULLY]")
    return {"hitl_status": "executed" if decision == "approved" else "rejected"}

# --- Graph Routing Logic ---

def route_from_planner(state: AgentState) -> Any:
    tasks = state.get("planner_tasks") or []
    mode = state.get("execution_mode") or "sequential"
    
    if mode == "parallel":
        parallel_nodes = []
        for t in tasks:
            agent = t.get("agent")
            if agent in ["candidate", "knowledge"]:
                parallel_nodes.append(agent)
        if parallel_nodes:
            return parallel_nodes
            
    if tasks:
        first_agent = tasks[0].get("agent")
        if first_agent == "action":
            return "action_planner"
        return first_agent
    return "action_planner"

def route_after_candidate(state: AgentState) -> str:
    tasks = state.get("planner_tasks") or []
    mode = state.get("execution_mode") or "sequential"
    
    if mode == "parallel":
        has_client = any(t.get("agent") == "client" for t in tasks)
        if has_client:
            return "client"
        return "action_planner"
    else:
        task_agents = [t.get("agent") for t in tasks]
        if "candidate" in task_agents:
            idx = task_agents.index("candidate")
            if idx + 1 < len(task_agents):
                next_agent = task_agents[idx + 1]
                if next_agent == "action":
                    return "action_planner"
                return next_agent
        return "client"

def route_after_client(state: AgentState) -> str:
    tasks = state.get("planner_tasks") or []
    mode = state.get("execution_mode") or "sequential"
    
    if mode == "parallel":
        return "action_planner"
    else:
        task_agents = [t.get("agent") for t in tasks]
        if "client" in task_agents:
            idx = task_agents.index("client")
            if idx + 1 < len(task_agents):
                next_agent = task_agents[idx + 1]
                if next_agent == "action":
                    return "action_planner"
                return next_agent
        return "knowledge"

def route_after_knowledge(state: AgentState) -> str:
    tasks = state.get("planner_tasks") or []
    mode = state.get("execution_mode") or "sequential"
    
    if mode == "parallel":
        has_client = any(t.get("agent") == "client" for t in tasks)
        if has_client:
            return "client"
        return "action_planner"
    else:
        task_agents = [t.get("agent") for t in tasks]
        if "knowledge" in task_agents:
            idx = task_agents.index("knowledge")
            if idx + 1 < len(task_agents):
                next_agent = task_agents[idx + 1]
                if next_agent == "action":
                    return "action_planner"
                return next_agent
        return "action_planner"

def route_after_score(state: AgentState):
    rec = state.get("top_recommendation", {})
    if not rec or not rec.get("job_id"):
        return END
    return "hitl"

def route_after_hitl(state: AgentState):
    return "execute"

# --- Build Refactored Platform Graph ---

builder = StateGraph(AgentState)
builder.add_node("planner", run_planner_node)
builder.add_node("candidate", run_candidate_node)
builder.add_node("client", run_client_node)
builder.add_node("knowledge", run_knowledge_node)
builder.add_node("action_planner", run_action_planner_node)
builder.add_node("hitl", hitl_gate)
builder.add_node("execute", execute_action)

builder.set_entry_point("planner")
builder.add_conditional_edges("planner", route_from_planner, {"candidate": "candidate", "knowledge": "knowledge", "client": "client", "action_planner": "action_planner"})
builder.add_conditional_edges("candidate", route_after_candidate, {"client": "client", "knowledge": "knowledge", "action_planner": "action_planner"})
builder.add_conditional_edges("client", route_after_client, {"knowledge": "knowledge", "action_planner": "action_planner"})
builder.add_conditional_edges("knowledge", route_after_knowledge, {"client": "client", "action_planner": "action_planner"})
builder.add_conditional_edges("action_planner", route_after_score, {"hitl": "hitl", END: END})
builder.add_conditional_edges("hitl", route_after_hitl, {"execute": "execute", END: END})
builder.add_edge("execute", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# --- BACKUP: Legacy DAG Graph Implementation (For Reference / Backup calls) ---

async def legacy_fetch_candidate(state: AgentState):
    candidate_id = state["candidate_id"]
    session_id = state.get("session_id") or f"session_{candidate_id}_{os.urandom(4).hex()}"
    cand = await mcp_call("get_candidate_profile", candidate_id=candidate_id)
    if not cand:
        return {"candidate_data": {}, "matched_jobs": [], "session_id": session_id}
    skills = ",".join(cand.get("skills", []))
    jobs = await mcp_call("search_job_descriptions", query_skills=skills)
    cache_set(f"analysis:{candidate_id}", {"candidate": cand, "jobs": jobs}, ttl=300)
    return {"candidate_data": cand, "matched_jobs": jobs or [], "session_id": session_id}

async def legacy_score_and_reason(state: AgentState):
    candidate = state["candidate_data"]
    jobs = state["matched_jobs"]
    if not candidate or not jobs:
        return {"top_recommendation": {}, "reasoning": "No matching open roles found.", "confidence": 0.0}
    history = await mcp_call("get_placement_history", candidate_id=state["candidate_id"])
    prompt = f"Analyze Candidate: {candidate.get('name')} against open jobs {jobs}. Past Placements: {history}."
    try:
        structured_llm = get_structured_llm(MatchRecommendation)
        result = await safe_ainvoke(structured_llm, prompt, session_id=state.get("session_id"), log_callback=log_event)
        parsed = {
            "job_id": result.job_id,
            "job_title": result.job_title,
            "client_name": result.client_name,
            "client_id": result.client_id,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
    except Exception:
        parsed = {"job_id": jobs[0]["id"], "job_title": jobs[0]["title"], "client_name": jobs[0]["clients"]["name"], "client_id": jobs[0]["client_id"], "confidence": 0.5, "reasoning": "Fallback match"}
    return {"top_recommendation": parsed, "reasoning": parsed.get("reasoning", ""), "confidence": parsed.get("confidence", 0.5)}

legacy_builder = StateGraph(AgentState)
legacy_builder.add_node("fetch", legacy_fetch_candidate)
legacy_builder.add_node("score", legacy_score_and_reason)
legacy_builder.add_node("hitl", hitl_gate)
legacy_builder.add_node("execute", execute_action)
legacy_builder.set_entry_point("fetch")
legacy_builder.add_edge("fetch", "score")
legacy_builder.add_conditional_edges("score", route_after_score, {"hitl": "hitl", END: END})
legacy_builder.add_conditional_edges("hitl", route_after_hitl, {"execute": "execute", END: END})
legacy_builder.add_edge("execute", END)

legacy_graph = legacy_builder.compile(checkpointer=memory)