
from enum import Enum

class Analysis_Status(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"

class Ticket_Status(str, Enum):
    IN_PROGRESS = "in_progress"
    OPEN        = "open"
    RESOLVED    = "resolved"
    CLOSED      = "closed"


# برای تیکت انالیز اضافه شده 
class Urgency_Status(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident_Status(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"

class Source_Status(str, Enum):
    MANUAL = "manual"
    CSV = "csv"

