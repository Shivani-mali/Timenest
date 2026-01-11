from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[str] = None
