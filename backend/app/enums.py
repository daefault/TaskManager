from enum import Enum

class NotificationType(str, Enum):
    TASK_ASSIGNED = 'task_assigned'
    USER_INACTIVE = 'user_inactive'
    
    def __str__(self):
        return self.value

class Status(str, Enum):
    ACTIVE='active'
    ARCHIVED = 'archived'

    def __str__(self):
        return self.value
    
class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'
    OVERDUE = 'overdue'

    def __str__(self):
        return self.value

class Priority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    
    def __str__(self):
        return self.value