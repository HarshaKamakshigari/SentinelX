"""
Incident Report Model — includes threat intelligence enrichment fields.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ThreatIntelReport(BaseModel):
    """Threat intelligence enrichment section of the incident report."""
    malware_family: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    vt_percent: Optional[float] = None
    source: Optional[str] = None


class IncidentReport(BaseModel):
    """Final SOC-style incident report with threat intelligence enrichment."""
    incident_id: str
    timestamp: str
    host: str
    summary: str
    severity: str
    confidence: float
    mitre_techniques: List[str] = []
    timeline: List[str] = []
    agents_invoked: List[str] = []
    details: Dict[str, Any] = {}
    threat_intelligence: Optional[ThreatIntelReport] = None
