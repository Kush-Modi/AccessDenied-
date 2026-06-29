from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class KnowledgeItem(BaseModel):
    id: str
    type: str
    source: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class RecruiterNote(BaseModel):
    id: str
    candidate_id: str
    notes: str
    created_at: Optional[datetime] = None

class MeetingNote(BaseModel):
    id: str
    client_id: str
    candidate_id: Optional[str] = None
    meeting_date: str
    notes: str
    created_at: Optional[datetime] = None

class Email(BaseModel):
    id: str
    sender: str
    recipient: str
    subject: Optional[str] = None
    body: str
    sent_at: Optional[datetime] = None

class CRMUpdate(BaseModel):
    id: str
    client_id: str
    update_text: str
    created_at: Optional[datetime] = None

class InterviewFeedback(BaseModel):
    id: str
    candidate_id: str
    jd_id: str
    feedback: str
    rating: int
    created_at: Optional[datetime] = None

class CustomerInteraction(BaseModel):
    id: str
    client_id: str
    candidate_id: Optional[str] = None
    interaction_date: str
    type: str
    notes: str
    created_at: Optional[datetime] = None
