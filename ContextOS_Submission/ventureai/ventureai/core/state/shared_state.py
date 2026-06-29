from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from core.execution.context import ExecutionContext

class SharedState(BaseModel):
    session_id: str
    candidate_id: str
    client_id: Optional[str] = None
    planner_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    candidate_context: Dict[str, Any] = Field(default_factory=dict)
    client_context: Dict[str, Any] = Field(default_factory=dict)
    knowledge_context: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0
    memory: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    hitl_status: str = ""
    pending_action: Dict[str, Any] = Field(default_factory=dict)
    future_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution metadata fields
    execution_context: ExecutionContext = Field(default_factory=ExecutionContext)
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    planner_reasoning: str = ""
