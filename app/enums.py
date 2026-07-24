from enum import Enum

class NotificationType(str, Enum):
    TASK_ASSIGNED = 'task_assigned'
    STATUS_CHANGED = 'status_changed'
    DEADLINE_REMINDER = 'deadline_reminder'


class Status(str, Enum):
    ACTIVE='active'
    ARCHIVED = 'archived'

class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'

class Priority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'