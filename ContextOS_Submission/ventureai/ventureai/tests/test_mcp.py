import sys
import os
import asyncio

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override standard python command to use active venv python interpreter
import mcp_client
mcp_client.SERVER_PARAMS.command = sys.executable

from mcp_client import mcp_call

async def main():
    print("--- Testing MCP Client-Server Communication ---")
    candidate_id = "a2f52625-84e2-4367-abc6-9eccca7b5e54"
    
    # test get_candidate_profile
    print("\nCalling get_candidate_profile...")
    profile = await mcp_call("get_candidate_profile", candidate_id=candidate_id)
    print(f"Result: {profile}")
    
    # test search_job_descriptions
    print("\nCalling search_job_descriptions...")
    jobs = await mcp_call("search_job_descriptions", query_skills="Python,AWS,Kubernetes")
    print(f"Result: {jobs}")
    
    # test log_recruiter_action
    print("\nCalling log_recruiter_action...")
    log_result = await mcp_call(
        "log_recruiter_action",
        action_type="test_action",
        target_id=candidate_id,
        target_type="candidate",
        reason="Testing MCP connection",
        recruiter_decision="approved"
    )
    print(f"Result: {log_result}")

if __name__ == "__main__":
    asyncio.run(main())
