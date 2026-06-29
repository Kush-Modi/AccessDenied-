import sys
import os
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field

# Core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.registry.base import BaseAgent
from core.llm_client import llm, safe_ainvoke, get_structured_llm
from core.react_runner import ReActRunner
from langchain_core.tools import tool

class TaskPlan(BaseModel):
    agent: str = Field(description="Agent name: candidate, client, knowledge, or action")
    goals: str = Field(description="Goal for this agent")
    priority: str = Field(description="high, medium, or low")
    expected_outputs: List[str] = Field(description="Expected outputs to write to shared state")
    termination_conditions: str = Field(description="Termination conditions for the agent")

class ExecutionPlan(BaseModel):
    execution_mode: str = Field(description="sequential or parallel")
    tasks: List[TaskPlan] = Field(description="List of tasks to execute")
    planner_reasoning: str = Field(description="Explanation of the chosen execution strategy")

@tool
def get_candidate_feedback_history(candidate_id: str) -> str:
    """Retrieve historical feedback and decisions for a candidate to check if they have past rejections or approved placements."""
    try:
        from memory.repository import MemoryRepository
        history = MemoryRepository.get_feedback_history(candidate_id=candidate_id)
        # Return a simplified string representation
        trace = []
        for h in history:
            trace.append({
                "recommendation_id": h.get("recommendation_id"),
                "decision": h.get("recruiter_decision"),
                "outcome": h.get("outcome"),
                "timestamp": h.get("created_at")
            })
        return json.dumps(trace)
    except Exception as e:
        return json.dumps([])

class PlannerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "planner"

    @property
    def description(self) -> str:
        return "Planner agent that dynamically determines required specialist agents and generates the execution plan using candidate history."

    @property
    def required_inputs(self) -> list[str]:
        return ["candidate_id"]

    @property
    def produced_outputs(self) -> list[str]:
        return ["planner_tasks", "planner_reasoning", "execution_mode"]

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get("candidate_id")
        session_id = state.get("session_id")
        
        # Tools available to the planner
        tools = [get_candidate_feedback_history]
        
        system_prompt = """You are orchestrating enterprise recruiting. Your goal is to formulate an execution plan for analyzing a candidate match.

IMPORTANT: You have ONLY ONE available tool: 'get_candidate_feedback_history'. Do NOT attempt to call any other tool name.

Use 'get_candidate_feedback_history' ONLY IF you need to check if the candidate has historical rejections or approvals.
Once you have gathered sufficient information (or if no tool call is needed), conclude your analysis.

Rules for planning:
- You MUST always schedule the 'candidate' agent as the first task to fetch the candidate profile and retrieve matched jobs.
- If a candidate has rejections/failures in their history -> You MUST include 'knowledge' agent in the plan with the goal of searching recruiter notes/emails/transcripts for rejection reasons.
- If the candidate has no problematic history, you may skip 'knowledge' and 'client' agents to keep the plan efficient.
- 'action' agent must always be the final task in the plan.
- If tasks are independent, you can set 'execution_mode' to 'sequential'.
"""
        
        # Format current context
        context_str = f"Candidate ID: {candidate_id}\nSession ID: {session_id}"
        
        # Run ReAct loop for planning phase
        react_log_callback = lambda sid, msg: state.get("log_callback", print)(msg)
        final_reply, scratchpad, updated_cache = await ReActRunner.run_loop(
            agent_name=self.name,
            system_prompt=system_prompt,
            tools_list=tools,
            state_context=context_str,
            session_id=session_id,
            goal="Formulate an execution plan using candidate history if required.",
            expected_outputs=["execution_mode", "tasks", "planner_reasoning"],
            termination_conditions="Plan formulated based on feedback history.",
            max_tool_calls=5,
            tool_cache=state.get("tool_cache", {}),
            log_callback=react_log_callback
        )
        
        # Now run structured LLM (Gemini preferred) to parse final execution plan from ReAct history
        structured_llm = get_structured_llm(ExecutionPlan)
        history_msgs = [f"ReAct Scratchpad:\n" + "\n".join(scratchpad)]
        
        prompt = f"""Based on the planning analysis below, produce the structured execution plan JSON:
{history_msgs}
"""
        try:
            plan = await safe_ainvoke(structured_llm, prompt, session_id=session_id, log_callback=state.get("log_callback"))
        except Exception:
            # Fallback default plan
            plan = ExecutionPlan(
                execution_mode="sequential",
                tasks=[
                    TaskPlan(agent="candidate", goals="Fetch candidate profile and match jobs", priority="high", expected_outputs=["candidate_context", "matched_jobs"], termination_conditions="Matched jobs retrieved"),
                    TaskPlan(agent="client", goals="Evaluate client health and preferences", priority="medium", expected_outputs=["client_context"], termination_conditions="Client health fetched"),
                    TaskPlan(agent="knowledge", goals="Retrieve interactions history", priority="medium", expected_outputs=["knowledge_context"], termination_conditions="RAG items fetched"),
                    TaskPlan(agent="action", goals="Generate final placement scoring recommendation", priority="high", expected_outputs=["top_recommendation"], termination_conditions="Match score finalized")
                ],
                planner_reasoning="Fallback plan generated due to parsing error."
            )
            
        # Convert plan tasks to list of dicts for state compatibility
        tasks_list = []
        for t in plan.tasks:
            tasks_list.append({
                "agent": t.agent,
                "goals": t.goals,
                "priority": t.priority,
                "expected_outputs": t.expected_outputs,
                "termination_conditions": t.termination_conditions
            })
            
        # === SAFETY VALIDATION: Enforce invariants ===
        # 1. candidate MUST always be first
        agent_names = [t["agent"] for t in tasks_list]
        if "candidate" not in agent_names:
            tasks_list.insert(0, {
                "agent": "candidate",
                "goals": "Fetch candidate profile and match jobs",
                "priority": "high",
                "expected_outputs": ["candidate_context", "matched_jobs"],
                "termination_conditions": "Matched jobs retrieved"
            })
        elif tasks_list[0]["agent"] != "candidate":
            # Move candidate to front
            cand_task = next(t for t in tasks_list if t["agent"] == "candidate")
            tasks_list = [cand_task] + [t for t in tasks_list if t["agent"] != "candidate"]

        # 2. action MUST always be last
        agent_names = [t["agent"] for t in tasks_list]
        if "action" not in agent_names:
            tasks_list.append({
                "agent": "action",
                "goals": "Generate final placement scoring recommendation",
                "priority": "high",
                "expected_outputs": ["top_recommendation"],
                "termination_conditions": "Match score finalized"
            })
        elif tasks_list[-1]["agent"] != "action":
            action_task = next(t for t in tasks_list if t["agent"] == "action")
            tasks_list = [t for t in tasks_list if t["agent"] != "action"] + [action_task]
            
        # Add to state scratchpads
        agent_scratchpads = state.get("agent_scratchpads") or {}
        agent_scratchpads[self.name] = scratchpad
        
        return {
            "planner_tasks": tasks_list,
            "planner_reasoning": plan.planner_reasoning,
            "execution_mode": plan.execution_mode,
            "agent_scratchpads": agent_scratchpads,
            "tool_cache": updated_cache
        }
