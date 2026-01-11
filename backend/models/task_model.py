from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None  # low | medium | high
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    id: Optional[str] = None
