from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NormalizedEvent(BaseModel):
    event_id: str
    timestamp: datetime

    host: Optional[str] = None
    user_id: Optional[str] = None

    process_name: Optional[str] = None
    command_line: Optional[str] = None

    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None

    file_hash: Optional[str] = None
    event_type: Optional[str] = None
