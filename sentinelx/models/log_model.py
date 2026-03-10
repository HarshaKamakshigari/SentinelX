from pydantic import BaseModel
from typing import Optional


class SecurityLog(BaseModel):
    """Incoming security log schema."""
    host: Optional[str] = None
    event_type: Optional[str] = None
    process_name: Optional[str] = None
    parent_process: Optional[str] = None
    command_line: Optional[str] = None
    source_ip: Optional[str] = None
    file_hash: Optional[str] = None
    file_name: Optional[str] = None
    destination_ip: Optional[str] = None
    user_id: Optional[str] = None
    raw_log: Optional[str] = None
