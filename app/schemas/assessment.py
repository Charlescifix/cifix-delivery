from pydantic import BaseModel
from typing import Dict, Any

class AssessmentWebhookPayload(BaseModel):
    student_id: int
    raw_score: float
    level: str
    domains: Dict[str, Any]