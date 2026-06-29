import sys
import os
from typing import Dict, Any, List
from langchain_core.tools import tool

# Core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.registry.base import BaseAgent
from core.react_runner import ReActRunner
from mcp_client import mcp_call

@tool
async def get_candidate_profile(candidate_id: str) -> dict:
    """Fetch the candidate profile by their unique ID, returning their name, email, skills, experience, current position, and resume."""
    return await mcp_call("get_candidate_profile", candidate_id=candidate_id)

@tool
async def search_job_descriptions(query_skills: str) -> list:
    """Search open job descriptions by matching comma-separated skill keywords. Returns a list of jobs."""
    return await mcp_call("search_job_descriptions", query_skills=query_skills)

@tool
async def get_candidate_placement_history(candidate_id: str) -> list:
    """Fetch the past placement and hire records for a specific candidate from the memory layer."""
    return await mcp_call("get_placement_history", candidate_id=candidate_id)


class CandidateAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "candidate"

    @property
    def description(self) -> str:
        return "Specialist agent that fetches candidate profile info and matches open job descriptions using an autonomous ReAct loop."

    @property
    def required_inputs(self) -> list[str]:
        return ["candidate_id"]

    @property
    def produced_outputs(self) -> list[str]:
        return ["candidate_context", "candidate_data", "matched_jobs", "agent_outputs", "tool_cache", "agent_scratchpads"]

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get("candidate_id")
        session_id = state.get("session_id")
        log_cb = state.get("log_callback", print)
        
        log_cb(f"    * [{self.name.upper()}] Starting deterministic candidate profiling for candidate ID: '{candidate_id}'")
        
        # 1. Fetch Candidate Profile
        log_cb(f"      Calling get_candidate_profile...")
        profile = await mcp_call("get_candidate_profile", candidate_id=candidate_id) or {}
        
        # 2. Extract skills and query jobs
        skills = profile.get("skills", [])
        log_cb(f"Skills inventory mapped: {skills}")
        log_cb(f"Candidate has {profile.get('experience_years', 0)} years of experience.")
        
        query_skills = ", ".join(skills) if isinstance(skills, list) else str(skills)
        log_cb(f"      Calling search_job_descriptions with query: '{query_skills}'...")
        matched_jobs = await mcp_call("search_job_descriptions", query_skills=query_skills) or []
        
        # 3. Fetch placement history
        log_cb(f"      Calling get_placement_history...")
        placement_history = await mcp_call("get_placement_history", candidate_id=candidate_id) or []
        
        # Build tool cache mimicking the react loop format so other agents/explainability are completely backwards compatible
        updated_cache = {**state.get("tool_cache", {})}
        updated_cache[f"get_candidate_profile:{{'candidate_id': '{candidate_id}'}}"] = profile
        updated_cache[f"search_job_descriptions:{{'query_skills': '{query_skills}'}}"] = matched_jobs
        updated_cache[f"get_placement_history:{{'candidate_id': '{candidate_id}'}}"] = placement_history
        
        candidate_context = {
            "profile": profile,
            "skills": skills,
            "experience_years": profile.get("experience_years", 0),
            "matched_jobs": matched_jobs
        }
        
        agent_outputs = state.get("agent_outputs") or {}
        agent_outputs["candidate"] = {
            "profile_fetched": bool(profile),
            "skills_count": len(skills),
            "matched_jobs_count": len(matched_jobs)
        }
        
        agent_scratchpads = state.get("agent_scratchpads") or {}
        agent_scratchpads[self.name] = [
            f"Fetched candidate profile for {candidate_id}.",
            f"Mapped candidate skills: {skills}.",
            f"Searched matched jobs: found {len(matched_jobs)} potential vacancies."
        ]
        
        return {
            "candidate_context": candidate_context,
            "candidate_data": profile,
            "matched_jobs": matched_jobs,
            "agent_outputs": agent_outputs,
            "tool_cache": updated_cache,
            "agent_scratchpads": agent_scratchpads
        }
