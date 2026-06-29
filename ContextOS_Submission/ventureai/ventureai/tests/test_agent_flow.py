import sys
import os
import asyncio

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import graph
from agent import graph

from agent import graph
from langgraph.types import Command

async def run_agent_test():
    candidate_id = "a2f52625-84e2-4367-abc6-9eccca7b5e54"
    session_id = f"test_agent_session_123"
    
    print("--- Starting Agent Graph ---")
    config = {"configurable": {"thread_id": session_id}}
    
    # 1. Run the graph up to the interrupt
    print("\n[Step 1] Invoking graph (fetching & scoring)...")
    result = await graph.ainvoke(
        {
            "candidate_id": candidate_id,
            "candidate_data": {},
            "matched_jobs": [],
            "top_recommendation": {},
            "reasoning": "",
            "confidence": 0.0,
            "hitl_status": "",
            "session_id": session_id,
        },
        config=config,
    )
    
    # Get current state to verify it paused
    state = await graph.aget_state(config)
    print(f"Current Graph State Next Node: {state.next}")
    print(f"Current State Values: reasoning: {state.values.get('reasoning')[:120]}...")
    print(f"Interrupt context: {state.tasks[0].interrupts if state.tasks else 'None'}")
    
    # 2. Resume graph from interrupt
    print("\n[Step 2] Resuming graph with decision: approved...")
    resume_result = await graph.ainvoke(
        Command(resume={"decision": "approved"}),
        config=config,
    )
    
    # Get final state to check action execution
    final_state = await graph.aget_state(config)
    print(f"Final Graph State Next Node: {final_state.next}")
    print(f"Final State Values: hitl_status: {final_state.values.get('hitl_status')}")

if __name__ == "__main__":
    asyncio.run(run_agent_test())
