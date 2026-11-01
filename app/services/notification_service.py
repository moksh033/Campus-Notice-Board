"""Notification logic. Owner: Mridul.

Notifications are rows in one shared table. Because students have no accounts, whether a
notification has been read is remembered per browser in session["read_notification_ids"].
"""
from flask import abort, session

from ..constants import NOTIFICATION_LIMIT
from ..extensions import db
from ..models import Announcement, Notification

_SESSION_KEY = "read_notification_ids"
_MAX_REMEMBERED = 200


def notify_published(announcement):
    """Create the notification for a published announcement. Safe to call repeatedly."""
    if not announcement.is_published:
        return None
    existing = Notification.query.filter_by(announcement_id=announcement.id).first()
    if existing:
        return existing
    message = f"New in {announcement.category}: {announcement.title}"[:200]
    notification = Notification(announcement_id=announcement.id, message=message)
    db.session.add(notification)
    db.session.commit()
    return notification


def remove_for(announcement_id):
    Notification.query.filter_by(announcement_id=announcement_id).delete()
    db.session.commit()


def list_recent(limit=NOTIFICATION_LIMIT):
    """Newest notifications whose announcement is still published."""
    return (
        Notification.query.join(Announcement, Notification.announcement_id == Announcement.id)
        .filter(Announcement.is_published.is_(True))
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(limit)
        .all()
    )


def read_ids():
    return set(session.get(_SESSION_KEY, []))


def unread_count(read=None):
    read = read_ids() if read is None else read
    return sum(1 for n in list_recent() if n.id not in read)


def _remember(ids):
    merged = list(dict.fromkeys(list(session.get(_SESSION_KEY, [])) + list(ids)))
    session[_SESSION_KEY] = merged[-_MAX_REMEMBERED:]
    session.modified = True


def mark_read(notification_id):
    if db.session.get(Notification, notification_id) is None:
        abort(404)
    _remember([notification_id])


def mark_all_read():
    _remember([n.id for n in list_recent()])
