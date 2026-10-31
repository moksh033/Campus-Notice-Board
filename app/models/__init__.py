"""Importing this package registers every table. Owner: Mihir."""
from .announcement import Announcement
from .attachment import Attachment
from .notification import Notification
from .publisher import Publisher

__all__ = ["Announcement", "Attachment", "Notification", "Publisher"]
