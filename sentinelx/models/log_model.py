from pydantic import BaseModel
from typing import Optional

class SecurityLog(BaseModel):
    """Incoming security log schema."""
    host: str
    event_type: str
    command_line: Optional[str] = None
    file_hash: Optional[str] = None
    destination_ip: Optional[str] = None
