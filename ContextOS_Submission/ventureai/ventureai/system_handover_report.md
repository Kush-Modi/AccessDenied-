# Master System Handover & Verification Report: Recruiter NBA Engine

This document outlines the final production-ready state of your **Next Best Action (NBA) Engine** backend slice. It describes the architecture, codebase file mapping, key features, and integration verification steps.

---

## 1. Core Architecture
The system consists of 4 decoupled layers operating on a dynamic, asynchronous state graph with a human approval interrupt gate.

```
                  [ Streamlit UI Dashboard ] (app_streamlit.py)
                            │              ▲
                            ▼              │
                      [ FastAPI API ] ──[ Redis Cache & Session Logs ]
                            │
                            ▼
                     [ LangGraph Agent ] (MemorySaver Checkpointer)
                            │
                            ▼  (Only communicates via MCP Protocol)
                     [ FastMCP Server ] (stdio transport)
                            │
                            ▼
                       [ Supabase ]
```

---

## 2. File-by-File Codebase Mapping

### Configuration & Base Clients
*   **`.env`**: Stores Supabase keys, Redis URLs, and Groq LLM API keys. (Copied to both the root directory and the `tests/` directory).
*   **`supabase_client.py`**: Connects to the Supabase PostgreSQL database. Calls `load_dotenv()` so it can resolve variables when run from subdirectories.
*   **`redis_client.py`**: Connects to the Redis cache with `decode_responses=True` to guarantee string outputs. Exports methods for caching candidate data (`cache_set`, `cache_get`), managing the state of pending approval cards (`set_hitl_pending`, `resolve_hitl`, `get_hitl_decision`), and streaming logs (`log_session`, `get_session_logs`).

### Model Context Protocol (MCP) Integration
*   **`mcp_server.py`**: Instantiates a `FastMCP` server over standard output streams. It exposes 5 specific recruiting tools wrapping database reads/writes:
    *   `get_candidate_profile(candidate_id)`: Fetches candidate skills/metadata.
    *   `get_client_account_health(client_id)`: Fetches account health metrics.
    *   `search_job_descriptions(query_skills)`: Searches open JDs matching skill criteria using LLM semantic matching.
    *   `get_placement_history(candidate_id, client_id)`: Inspects historical placements.
    *   `log_recruiter_action(...)`: Inserts recruiter action choices (approved/rejected) into Supabase.
*   **`mcp_client.py`**: A python wrapper that dynamically spawns the MCP server subprocess and executes tool requests asynchronously.

### Agent Brain ([agent.py](file:///s:/ventureai/agent.py))
The engine uses an **Autonomous ReAct Graph** utilizing LLM tool binding:
1.  **Pydantic Parser (`MatchRecommendation`)**: Implements strict structured outputs containing `job_id`, `job_title`, `client_name`, `client_id`, `confidence`, and `reasoning`.
2.  **`run_llm_agent` Node**: Binds the proxy tools (`get_candidate_profile`, `search_job_descriptions`, `get_placement_history`) to the `ChatGroq` LLM. The LLM dynamically calls tools in a loop to construct the candidate context.
3.  **`call_tools` Node**: Automatically runs tool actions requested by the LLM via MCP and passes back data.
4.  **`format_recommendation` Node**: Re-evaluates matches and invokes LLM structured parsing. Uses a mathematically structured scoring rubric to calculate candidate confidence scores.
5.  **`hitl_gate` Node**: Saves the card to Redis, sends an `interrupt()` to pause the graph, and saves the state to `MemorySaver()`.
6.  **`execute_action` Node**: Processes final decisions.
    *   *If Approved:* Logs the action to Supabase and caches the pitch to the active Next Best Action queue (`nba:{id}`) with status `approved`.
    *   *If Rejected:* Logs the action to Supabase (for model learning) and caches it under `nba:{id}` with status `rejected`.
7.  **Routing Nodes**:
    *   `route_agent`: Decides to keep calling tools or format recommendations.
    *   `route_after_score`: Bypasses the approval gate entirely if no matching open roles are found, sending the thread directly to `END`.
    *   `route_after_hitl`: Safely routes all approvals and rejections through the execution node to log results before ending.

### API Gateway ([main.py](file:///s:/ventureai/main.py))
FastAPI server hosting endpoints:
*   `GET /health`: Health status.
*   `POST /analyze`: Launches the agent. Includes a **Cache Check** that skips graph executions if a candidate has already been approved or rejected.
*   `GET /hitl/pending/{session_id}`: Returns the pending match card data from Redis.
*   `POST /hitl/respond`: Resumes the agent thread using `Command(resume=...)`. Includes an **Interrupt Guard** checking if the thread is actually interrupted, returning `400 Bad Request` if the session was already completed.
*   `GET /logs/{session_id}`: Retrieves the session's execution logs from Redis.
*   `GET /nba/queue`: Returns all cached Next Best Actions sorted by confidence (filtered to only show approved recommendations).

### Recruiter UI Dashboard ([app_streamlit.py](file:///s:/ventureai/app_streamlit.py))
A web-based interface built in Streamlit.
*   **Candidate Workspace Sidebar:** Fetches all candidate records from Supabase and shows selected candidate details (skills, experience, resume summary).
*   **ReAct Agent Logs Monitor:** Streams live agent execution logs step-by-step from Redis during analysis.
*   **Evaluation Decision Card:** Shows the computed match details and LLM evaluation reports.
*   **Approval & Rejection Gates:** Recruiter buttons to Approve/Reject pitches.
*   **Next Best Action Feed:** A ranked feed displaying approved candidate placements.

---

## 3. End-to-End Test Suite (`tests/`)

*   **`test_supabase.py`**: Verifies Supabase credentials and queries all 5 tables.
*   **`test_redis.py`**: Verifies Redis caching operations and state bridges.
*   **`test_mcp.py`**: Confirms MCP server stdio activation and tool calling logic.
*   **`test_agent_flow.py`**: Tests the isolated graph nodes, interrupts, and resuming states.
*   **`test_api.py`**: Uses FastAPI `TestClient` to run mock integrations through the complete ASGI REST loop.
*   **`test_candidate_karthik.py`**: Verifies routing when zero job matches exist (retains `no_match_found` status without pausing).
*   **`test_candidate_divya.py`**: Tests a complete loop (Analyze $\rightarrow$ Card Poll $\rightarrow$ Approve $\rightarrow$ Queue Update) for Candidate Divya.

---

## 4. Live Log Trace Verification

### Normal Approval Flow Trace:
```text
>>> [AGENT COORDINATOR] Evaluating candidate ID: a2f52625-84e2-4367-abc6-9eccca7b5e54
    - LLM requested tool call: get_candidate_profile with args: {'candidate_id': 'a2f52625-84e2-4367-abc6-9eccca7b5e54'}
    >>> [MCP CLIENT] Executing get_candidate_profile with parameters: {'candidate_id': 'a2f52625-84e2-4367-abc6-9eccca7b5e54'}
    <<< [MCP CLIENT] Finished execution of get_candidate_profile.
    
    - LLM requested tool call: search_job_descriptions with args: {'query_skills': 'Python,AWS,Kubernetes,Docker'}
    >>> [MCP CLIENT] Executing search_job_descriptions with parameters: {'query_skills': 'Python,AWS,Kubernetes,Docker'}
    <<< [MCP CLIENT] Finished execution of search_job_descriptions.
    
    - LLM decided no further tools are needed. Proceeding to format recommendation.
>>> [RECOMMENDATION FORMATTER] Extracting tool data & generating structured evaluation...
    - Structured Recommendation Generated: Senior DevOps Engineer at TechCorp (Confidence: 1.0)
    
>>> [HITL APPROVAL GATE] Saving pending recommendation for Ananya Sharma to Redis...
    !!! GRAPH PAUSED. Awaiting recruiter response (Approve/Reject)...

<<< GRAPH RESUMED. Recruiter decision received: APPROVED
>>> [ACTION EXECUTION] Processing final decision: approved
    - Logging recruiter action (approved) to Supabase 'recruiter_actions' table...
    - Caching finalized Next Best Action to Redis key: nba:a2f52625-84e2-4367-abc6-9eccca7b5e54
>>> [WORKFLOW COMPLETED SUCCESSFULLY]
```

### Rejection Flow Trace:
```text
<<< GRAPH RESUMED. Recruiter decision received: REJECTED
>>> [ACTION EXECUTION] Processing final decision: rejected
    - Logging recruiter action (rejected) to Supabase 'recruiter_actions' table...
    - Action rejected. Caching rejection status to Redis key: nba:90216606-920f-4f8c-9222-541ac0d4271c
>>> [WORKFLOW COMPLETED SUCCESSFULLY]
```
