from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ExecutionContext(BaseModel):
    current_task: Optional[str] = None
    current_agent: Optional[str] = None
    completed_agents: List[str] = Field(default_factory=list)
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    execution_timing: Dict[str, float] = Field(default_factory=dict)
    planner_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    future_replay_support: Dict[str, Any] = Field(default_factory=dict)
