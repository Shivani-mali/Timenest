from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Habit:
    name: str
    frequency: str  # daily | weekly | custom
    streak: int = 0
    last_completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    id: Optional[str] = None
