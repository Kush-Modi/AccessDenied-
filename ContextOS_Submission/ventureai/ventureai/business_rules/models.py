from pydantic import BaseModel
from typing import List, Optional

class Rule(BaseModel):
    id: str
    name: str
    description: str
    condition: str
    action: str
    weight: float = 0.0
    enabled: bool = True
    version: str = "1.0"

class RuleExecutionResult(BaseModel):
    rule_id: str
    name: str
    description: str
    action: str
    weight: float
    applied: bool
    explanation: str
    score_adjustment: float
