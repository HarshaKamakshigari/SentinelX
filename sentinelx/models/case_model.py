from pydantic import BaseModel
from typing import List, Optional

class IncidentReport(BaseModel):
    """Final SOC-style incident report."""
    incident_id: str
    summary: str
    severity: str
    confidence: float
    mitre_techniques: List[str] = []
    timeline: List[str] = []
    agents_invoked: List[str] = []
