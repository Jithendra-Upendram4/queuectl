from dataclasses import dataclass
from datetime import datetime

@dataclass
class Job:
    id: str
    command: str
    state: str = "pending"
    attempts: int = 0
    max_retries: int = 3
    created_at: str = None
    updated_at: str = None
    next_run_at: int = 0
    last_error: str | None = None
    output: str | None = None
    timeout: int | None = None

    def __post_init__(self):
        now = datetime.utcnow().isoformat() + "Z"
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if isinstance(self.next_run_at, float):
            self.next_run_at = int(self.next_run_at)

    def to_row(self):
        return (
            self.id, self.command, self.state, self.attempts,
            self.max_retries, self.created_at, self.updated_at,
            int(self.next_run_at), self.last_error, self.output, self.timeout
        )
