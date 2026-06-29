import time
import sys
from typing import List, Dict, Any, Tuple
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import BaseTool
from core.llm_client import llm, safe_ainvoke

class ReActRunner:
    @staticmethod
    async def run_loop(
        agent_name: str,
        system_prompt: str,
        tools_list: List[BaseTool],
        state_context: str,
        session_id: str,
        goal: str,
        expected_outputs: List[str] = None,
        termination_conditions: str = None,
        max_tool_calls: int = 6,
        tool_cache: Dict[str, Any] = None,
        log_callback = None
    ) -> Tuple[AIMessage, List[str], Dict[str, Any]]:
        """
        Runs an autonomous ReAct loop for a specialist agent.
        
        Returns:
            Tuple[AIMessage, List[str], Dict[str, Any]]:
                - The final AIMessage containing the agent's output.
                - A list of scratchpad entries (thoughts, actions, observations).
                - The updated tool_cache dictionary.
        """
        if tool_cache is None:
            tool_cache = {}
            
        # Log start
        if log_callback:
            log_callback(session_id, f"    * [{agent_name.upper()} REACT LOOP] Starting loop with goal: '{goal}'")
            
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools_list)
        
        # Build prompt
        full_system_prompt = f"""{system_prompt}

Planner Goal for this agent: {goal}
Expected Outputs: {expected_outputs or []}
Termination Conditions: {termination_conditions or 'Goal satisfied or sufficient information collected.'}

You operate in a strict ReAct loop:
1. Reason about what you need to do to satisfy the goal.
2. Select and call the appropriate tool.
3. Observe the tool's result.
4. Repeat or conclude.

Strict constraints:
- Do NOT make duplicate tool calls with the exact same arguments.
- Stop immediately when you have gathered all necessary information to fulfill the expected outputs.
- Limit yourself to a maximum of {max_tool_calls} tool calls.
"""

        messages = [
            SystemMessage(content=full_system_prompt),
            HumanMessage(content=f"Current State Context:\n{state_context}\n\nBegin your analysis.")
        ]
        
        scratchpad = []
        tool_call_count = 0
        blocked_call_count = 0
        executed_tool_signatures = set()
        
        final_response = None
        
        for step in range(max_tool_calls + 2):
            if log_callback:
                log_callback(session_id, f"      [Step {step + 1}] Invoking reasoning model...")
                
            response = await safe_ainvoke(llm_with_tools, messages, session_id=session_id, log_callback=log_callback)
            messages.append(response)
            final_response = response
            
            # Log Model Thought
            thought = response.content or ""
            if thought:
                cleaned_thought = thought.strip()
                if log_callback:
                    log_callback(session_id, f"      Thought: {cleaned_thought[:180]}...")
                scratchpad.append(f"Thought: {cleaned_thought}")
                
            # If no tool calls are requested, the agent believes it has finished
            if not response.tool_calls:
                if log_callback:
                    log_callback(session_id, "      Decision: Sufficiency condition met. Terminating ReAct loop.")
                scratchpad.append("Decision: Sufficiency condition met. Terminating.")
                break
                
            # Process tool calls
            tool_calls_to_process = response.tool_calls
            
            # Cap check BEFORE processing
            if tool_call_count >= max_tool_calls:
                if log_callback:
                    log_callback(session_id, f"      Warning: Maximum tool call limit ({max_tool_calls}) reached. Terminating.")
                scratchpad.append("Decision: Tool limit reached. Terminating.")
                break
                
            for tool_call in tool_calls_to_process:
                name = tool_call["name"]
                args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Check for duplicate signature
                sig = f"{name}:{str(sorted(args.items()))}"
                if sig in executed_tool_signatures:
                    blocked_call_count += 1
                    obs_str = f"You already called '{name}' with the same arguments. Do not repeat this call. Either call a DIFFERENT tool or conclude your analysis."
                    if log_callback:
                        log_callback(session_id, f"      Blocked Action: Duplicate call to '{name}' (blocked={blocked_call_count})")
                    scratchpad.append(f"Action (Blocked): Duplicate call to {name}")
                    scratchpad.append(f"Observation: {obs_str}")
                    messages.append(ToolMessage(content=obs_str, name=name, tool_call_id=tool_id))
                    # Count blocked calls against the limit to prevent infinite loops
                    if blocked_call_count >= 3:
                        if log_callback:
                            log_callback(session_id, f"      Warning: Too many duplicate calls. Terminating ReAct loop.")
                        scratchpad.append("Decision: Duplicate call limit reached. Terminating.")
                        return final_response, scratchpad, tool_cache
                    continue
                    
                executed_tool_signatures.add(sig)
                tool_call_count += 1
                
                if log_callback:
                    log_callback(session_id, f"      Action: Invoke tool '{name}' with arguments: {args}")
                scratchpad.append(f"Action: Call {name} with args {args}")
                
                # Check Tool Cache
                cache_key = f"{name}:{str(args)}"
                if cache_key in tool_cache:
                    if log_callback:
                        log_callback(session_id, f"      Cache Hit: Retrieving cached output for '{name}'")
                    observation_result = tool_cache[cache_key]
                else:
                    # Find tool
                    tool_obj = next((t for t in tools_list if t.name == name), None)
                    if tool_obj:
                        try:
                            # Invoke tool
                            observation_result = await tool_obj.ainvoke(args)
                        except Exception as e:
                            observation_result = f"Error executing tool: {str(e)}"
                    else:
                        observation_result = f"Error: Tool '{name}' not found."
                        
                    # Save to cache
                    tool_cache[cache_key] = observation_result
                    
                obs_str = str(observation_result)
                # Truncate large observations to avoid context overflow
                truncated_obs = obs_str[:800] + "... [truncated]" if len(obs_str) > 800 else obs_str
                if log_callback:
                    log_callback(session_id, f"      Observation: {truncated_obs[:220]}")
                scratchpad.append(f"Observation: {truncated_obs}")
                messages.append(ToolMessage(content=truncated_obs, name=name, tool_call_id=tool_id))
                
        return final_response, scratchpad, tool_cache
