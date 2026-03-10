from pydantic import BaseModel
from typing import Optional

class SecurityLog(BaseModel):
    """Incoming security log schema."""
    host: Optional[str] = None
    event_type: Optional[str] = None
    command_line: Optional[str] = None
    file_hash: Optional[str] = None
    destination_ip: Optional[str] = None
    raw_log: Optional[str] = None
