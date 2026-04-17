from app.database import Base  # noqa: F401

from app.models.user import User, UserRole  # noqa: F401
from app.models.municipio import Municipio  # noqa: F401
from app.models.parecer import (  # noqa: F401
    ParecerRequest, ParecerVersion, Attachment, ParecerStatusHistory,
    ParecerStatus, ParecerTema, ParecerModelo, VersionSource,
    ExtractionMethod, ExtractionStatus,
    PeerReview, PeerReviewStatus,
)
from app.models.movement import Process, ProcessLawyer, Movement, MovementType  # noqa: F401
from app.models.task import Board, Column, Task, TaskHistory, TaskCategory, TaskPriority  # noqa: F401
from app.models.notification import Notification, Holiday, NotificationChannel, NotificationStatus  # noqa: F401
from app.models.system_config import SystemConfig  # noqa: F401

__all__ = [
    "Base",
    "User", "UserRole",
    "Municipio",
    "ParecerRequest", "ParecerVersion", "Attachment", "ParecerStatusHistory",
    "ParecerStatus", "ParecerTema", "ParecerModelo", "VersionSource",
    "ExtractionMethod", "ExtractionStatus",
    "PeerReview", "PeerReviewStatus",
    "Process", "ProcessLawyer", "Movement", "MovementType",
    "Board", "Column", "Task", "TaskHistory", "TaskCategory", "TaskPriority",
    "Notification", "Holiday", "NotificationChannel", "NotificationStatus",
    "SystemConfig",
]
