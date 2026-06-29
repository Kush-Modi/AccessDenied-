from typing import List, Dict, Any, Optional

class EvidenceNode:
    def __init__(
        self,
        node_type: str,
        title: str,
        description: str,
        score: float,
        source_id: Optional[str] = None,
        children: Optional[List['EvidenceNode']] = None
    ):
        self.node_type = node_type # e.g. "Recommendation", "Evidence", "Meeting Note", "CRM Update", "Recruiter Note", "Placement History", "Business Signal"
        self.title = title
        self.description = description
        self.score = score
        self.source_id = source_id # ID of the record if it maps to a DB row
        self.children = children or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.node_type,
            "title": self.title,
            "description": self.description,
            "score": round(self.score, 4),
            "source_id": self.source_id,
            "children": [c.to_dict() for c in self.children]
        }
