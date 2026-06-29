import sys
import os
import json
from typing import Dict, Any, List
from langchain_core.tools import tool

# Core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.registry.base import BaseAgent
from core.react_runner import ReActRunner
from core.llm_client import llm, MatchRecommendation, safe_ainvoke, get_structured_llm
from core.config_loader import ConfigLoader
from mcp_client import mcp_call
from explainability.scoring import DecisionScorer
from explainability.formatter import ExplainabilityFormatter

@tool
async def get_action_placement_history(candidate_id: str = None, client_id: str = None) -> list:
    """Fetch the past placement and hire records for a specific candidate or client from the memory layer."""
    return await mcp_call("get_placement_history", candidate_id=candidate_id, client_id=client_id)

@tool
async def get_action_client_health(client_id: str) -> dict:
    """Fetch profile data, account health score, and hiring preferences for a client company by its UUID."""
    return await mcp_call("get_client_account_health", client_id=client_id)


class ActionPlannerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "action"

    @property
    def description(self) -> str:
        return "Specialist agent that scores candidate fit, running threshold-driven evidence collection loops."

    @property
    def required_inputs(self) -> list[str]:
        return ["candidate_data", "matched_jobs"]

    @property
    def produced_outputs(self) -> list[str]:
        return [
            "top_recommendation", "reasoning", "confidence",
            "agent_outputs", "tool_cache", "agent_scratchpads",
            "knowledge_trace", "evidence_tree", "retrieval_trace",
            "planner_trace", "decision_trace", "business_rule_trace",
            "memory_trace", "confidence_breakdown"
        ]

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_data = state.get("candidate_data") or {}
        matched_jobs = state.get("matched_jobs") or []
        candidate_id = state.get("candidate_id")
        session_id = state.get("session_id")
        
        if not candidate_data or not matched_jobs:
            reasoning = "No matching open roles found."
            return {
                "top_recommendation": {},
                "reasoning": reasoning,
                "confidence": 0.0,
                "agent_outputs": {
                    "action": {
                        "success": False,
                        "reason": "No candidate data or matched jobs found."
                    }
                }
            }
            
        # Get threshold from ranking_config.yaml
        config = ConfigLoader.get_config()
        confidence_threshold = config.get("retrieval", {}).get("similarity_threshold", 0.70)
        
        # 1. Attempt initial recommendation generation using available evidence
        messages = state.get("messages") or []
        history_msgs = [msg.content for msg in messages if hasattr(msg, "content")]
        if not history_msgs:
            history_msgs = [f"Analyze candidate profile for candidate ID: {candidate_id}"]
            
        prompt = f"""
You are an expert executive recruiter. Perform a detailed, highly professional match analysis between the candidate and the matching jobs.

Candidate Profile:
- Name: {candidate_data.get('name')}
- Current Position: {candidate_data.get('current_position', 'N/A')}
- Skills: {', '.join(candidate_data.get('skills', []))}
- Experience: {candidate_data.get('experience_years', 0)} years
- Resume: {candidate_data.get('resume_text', 'N/A')}

Matching Open Jobs:
{json.dumps(matched_jobs, indent=2, default=str)}

Analysis Context History:
{history_msgs}

Pick the SINGLE best job match. In the 'confidence' field, calculate the score mathematically based on this rubric:
1. SKILL ALIGNMENT (Max 0.40): Calculate the ratio of candidate matching skills to the job required skills.
2. EXPERIENCE FIT (Max 0.30): Compare candidate experience years to job requirements (Full 0.30 if equal/greater, partial if less).
3. PLACEMENT EVIDENCE (Max 0.20): Award up to 0.20 if candidate has successful historical placements in this role or at this client.
4. LOCATION & STATUS (Max 0.10): Award 0.10 if locations match (Bangalore/Remote etc) and they are available.

Sum these 4 components to calculate the final 'confidence' score (between 0.0 and 1.0).

In the 'reasoning' field, format your output as a professional report using this exact template structure:
[MATCH FIT]: [A 2-sentence summary of why the candidate is a fit for the role]
[KEY STRENGTHS]:
- [Bullet 1: Direct skill/experience alignment]
- [Bullet 2: Specific context or project match]
[PLACEMENT EVIDENCE]: [Reference the past placement records for this candidate or client, explaining how previous success reduces hiring risk]
[GAPS & MITIGATION]: [Specify any missing skills or experience gaps, and explain how the candidate can adapt or upskill]
[RECRUITER PITCH HOOK]: [A one-sentence persuasive statement the recruiter can read to pitch this candidate to the client's hiring manager]
"""
        
        # Log UI expected markers
        state.get("log_callback", print)("[ACTION PLANNER] Assembling evidence...")
        
        try:
            structured_llm = get_structured_llm(MatchRecommendation)
            initial_rec = await safe_ainvoke(structured_llm, prompt, session_id=session_id, log_callback=state.get("log_callback"))
            confidence = initial_rec.confidence
            reasoning = initial_rec.reasoning
            job_id = initial_rec.job_id
            client_id = initial_rec.client_id
            client_name = initial_rec.client_name
            job_title = initial_rec.job_title
        except Exception as e:
            # Fallback
            fallback_job = matched_jobs[0]
            client_name = "Client"
            if "clients" in fallback_job and isinstance(fallback_job["clients"], dict):
                client_name = fallback_job["clients"].get("name", "Client")
            confidence = fallback_job.get("match_score", 0.5)
            reasoning = f"Strong skill match: {fallback_job.get('match_score', 0):.0%} overlap"
            job_id = fallback_job["id"]
            client_id = fallback_job["client_id"]
            job_title = fallback_job["title"]
            
        # 2. Check if confidence score meets the threshold
        scratchpad = []
        updated_cache = state.get("tool_cache", {})
        
        if confidence < confidence_threshold:
            state.get("log_callback", print)(f"Initial confidence score ({confidence:.2f}) is below threshold ({confidence_threshold:.2f}). Triggering autonomous evidence collection loop...")
            
            # Tools
            tools = [get_action_placement_history, get_action_client_health]
            
            system_prompt = f"""You are the Decision Scorer specialist.
The initial match confidence for the candidate is {confidence:.2f}, which is below the threshold of {confidence_threshold:.2f}.
Use your tools to query client account health and placement history.
Gather additional evidence to confirm or adjust the confidence rating.
"""
            react_log_callback = lambda sid, msg: state.get("log_callback", print)(msg)
            final_reply, scratchpad, updated_cache = await ReActRunner.run_loop(
                agent_name=self.name,
                system_prompt=system_prompt,
                tools_list=tools,
                state_context=f"Candidate ID: {candidate_id}\nClient ID: {client_id}\nJob ID: {job_id}",
                session_id=session_id,
                goal=f"Determine if historical placement context boosts or changes match rating.",
                expected_outputs=["final_recommendation"],
                termination_conditions="Additional evidence analyzed.",
                max_tool_calls=5,
                tool_cache=updated_cache,
                log_callback=react_log_callback
            )
            
            # Now run structured LLM one final time, incorporating the new scratchpad observations
            prompt_with_evidence = f"""
{prompt}

Additional Evidence Gathered during ReAct loop:
{"/n".join(scratchpad)}

Generate the final structured recommendation based on this full body of evidence.
"""
            try:
                final_rec = await safe_ainvoke(structured_llm, prompt_with_evidence, session_id=session_id, log_callback=state.get("log_callback"))
                confidence = final_rec.confidence
                reasoning = final_rec.reasoning
                job_id = final_rec.job_id
                client_id = final_rec.client_id
                client_name = final_rec.client_name
                job_title = final_rec.job_title
            except Exception:
                pass
        else:
            state.get("log_callback", print)(f"Initial confidence score ({confidence:.2f}) satisfies threshold. Skipping ReAct evidence search.")
            scratchpad = ["Initial confidence satisfied threshold. No additional tool calls required."]

        # 3. Post-Processing: Run Rules Engine, Memory, and Decision Scorer
        # Find job description details in matched_jobs
        job_data = next((j for j in matched_jobs if j.get("id") == job_id), matched_jobs[0] if matched_jobs else {})
        
        # Fetch client health
        client_data = {}
        for k, v in updated_cache.items():
            if k.startswith("get_client_account_health:") and client_id in k:
                client_data = v
                break
        if not client_data:
            # Check for candidate agent client cached details
            client_ctx = state.get("client_context") or {}
            if client_id in client_ctx:
                client_data = client_ctx[client_id].get("profile", {})
        if not client_data:
            try:
                client_data = await mcp_call("get_client_account_health", client_id=client_id) or {}
            except Exception:
                client_data = {}
                
        # Fetch planner memory context
        from memory.planner_memory import PlannerMemory
        try:
            memory_context = PlannerMemory.get_memory_context(
                candidate_id=candidate_id,
                client_id=client_id,
                job_id=job_id
            )
        except Exception:
            memory_context = {}

        # Run Business Rules Engine
        from business_rules.engine import BusinessRulesEngine
        from business_rules.evaluator import RuleEvaluator
        
        # Log UI expected marker
        state.get("log_callback", print)("Running Business Rules Engine validation...")
        
        try:
            rule_context = RuleEvaluator.build_context(
                candidate=candidate_data,
                client=client_data,
                job=job_data,
                extra={
                    "candidate_rejected_recently": memory_context.get("failure_rate", 0.0) > 0.0 or any(h.get("decision") == "rejected" for h in memory_context.get("history_trace", [])),
                    "candidate_already_submitted": any(h.get("decision") == "approved" for h in memory_context.get("history_trace", [])),
                }
            )
            rules_engine = BusinessRulesEngine()
            business_rules_res = rules_engine.run(rule_context)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to run business rules engine: {e}\n")
            business_rules_res = {}
            
        # Calculate final Decision Intelligence Confidence and build Evidence Tree
        knowledge_context = state.get("knowledge_context") or {}
        ranked_items = knowledge_context.get("ranked_items", [])
        client_health_score = float(client_data.get("account_health_score", client_data.get("account_health", 60))) / 100.0
        
        # Calculate Priority/Urgency Score
        desc_text = str(job_data.get("description_text", "")).lower()
        title_text = str(job_data.get("title", "")).lower()
        if "critical" in desc_text or "critical" in title_text or "urgent" in desc_text or "urgent" in title_text:
            priority_urgency_score = 1.0
        elif "high" in desc_text or "high" in title_text:
            priority_urgency_score = 0.8
        elif "medium" in desc_text:
            priority_urgency_score = 0.5
        else:
            priority_urgency_score = 0.3

        decision = DecisionScorer.calculate_decision(
            candidate_fit_score=confidence,
            ranked_knowledge_items=ranked_items,
            candidate_name=candidate_data.get("name", "Candidate"),
            client_name=client_name,
            jd_title=job_title,
            business_rules_res=business_rules_res,
            memory_context=memory_context,
            client_health=client_health_score,
            priority_urgency_score=priority_urgency_score
        )
        
        planner_steps = [
            "Task Planning initiated",
            "Fetched candidate profile context",
            "Executed semantic match against open jobs",
            "Fetched client account details & health metrics",
            "Loaded history from Planner Memory feedback logs",
            "Executed Business Rules Engine validation",
            "Compiled final multi-signal decision confidence score"
        ]
        
        explanation = ExplainabilityFormatter.format_explanation(decision, ranked_items, planner_steps)
        
        final_conf = decision["final_confidence"]
        
        # Package top recommendation trace fields
        top_recommendation = {
            "job_id": job_id,
            "job_title": job_title,
            "client_name": client_name,
            "client_id": client_id,
            "confidence": final_conf,
            "decision_confidence": final_conf,
            "reasoning": f"{reasoning}\n\n{explanation['markdown_explanation']}",
            "knowledge_trace": explanation["knowledge_trace"],
            "retrieval_trace": explanation["retrieval_trace"],
            "planner_trace": explanation["planner_trace"],
            "decision_trace": explanation["decision_trace"],
            "business_rule_trace": explanation["business_rule_trace"],
            "memory_trace": explanation["memory_trace"],
            "evidence_tree": explanation["evidence_tree"],
            "confidence_breakdown": explanation["confidence_breakdown"]
        }
        
        agent_outputs = state.get("agent_outputs") or {}
        agent_outputs["action"] = {
            "success": True,
            "job_title": job_title,
            "client_name": client_name,
            "confidence": final_conf,
            "knowledge_trace": explanation["knowledge_trace"],
            "retrieval_trace": explanation["retrieval_trace"],
            "planner_trace": explanation["planner_trace"],
            "decision_trace": explanation["decision_trace"],
            "business_rule_trace": explanation["business_rule_trace"],
            "memory_trace": explanation["memory_trace"]
        }
        
        agent_scratchpads = state.get("agent_scratchpads") or {}
        agent_scratchpads[self.name] = scratchpad
        
        return {
            "top_recommendation": top_recommendation,
            "reasoning": top_recommendation["reasoning"],
            "confidence": final_conf,
            "knowledge_trace": explanation["knowledge_trace"],
            "retrieval_trace": explanation["retrieval_trace"],
            "planner_trace": explanation["planner_trace"],
            "decision_trace": explanation["decision_trace"],
            "business_rule_trace": explanation["business_rule_trace"],
            "memory_trace": explanation["memory_trace"],
            "evidence_tree": explanation["evidence_tree"],
            "confidence_breakdown": explanation["confidence_breakdown"],
            "agent_outputs": agent_outputs,
            "tool_cache": updated_cache,
            "agent_scratchpads": agent_scratchpads
        }
