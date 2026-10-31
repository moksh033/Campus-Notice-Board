"""Announcement business logic. Owner: Mihir.

Routes call these functions; these functions talk to the database.
"""
import re
from datetime import date, time

from flask import abort

from ..constants import CATEGORIES, LINK_MAX, TITLE_MAX, VENUE_MAX
from ..errors import ValidationError
from ..extensions import db, utcnow
from ..models import Announcement
from . import attachment_service, notification_service

_LINK_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


def _text(value):
    return (value or "").strip()


def _to_date(value, errors):
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        errors["event_date"] = "Event date must look like 2026-12-31."
        return None


def _to_time(value, errors):
    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    try:
        return time.fromisoformat(str(value).strip())
    except ValueError:
        errors["event_time"] = "Event time must look like 14:30."
        return None


def validate_announcement_data(data):
    """Check and clean the user's input. Raises ValidationError, or returns clean fields."""
    errors = {}

    title = _text(data.get("title"))
    if not title:
        errors["title"] = "Title is required."
    elif len(title) > TITLE_MAX:
        errors["title"] = f"Title must be {TITLE_MAX} characters or fewer."

    description = _text(data.get("description"))
    if not description:
        errors["description"] = "Description is required."

    category = _text(data.get("category"))
    if category not in CATEGORIES:
        errors["category"] = "Category must be one of: " + ", ".join(CATEGORIES) + "."

    venue = _text(data.get("venue")) or None
    if venue and len(venue) > VENUE_MAX:
        errors["venue"] = f"Venue must be {VENUE_MAX} characters or fewer."

    link = _text(data.get("registration_link")) or None
    if link and (len(link) > LINK_MAX or not _LINK_PATTERN.match(link)):
        errors["registration_link"] = "Registration link must start with http:// or https://."

    event_date = _to_date(data.get("event_date"), errors)
    event_time = _to_time(data.get("event_time"), errors)

    if errors:
        raise ValidationError(errors)

    return {
        "title": title,
        "description": description,
        "category": category,
        "venue": venue,
        "registration_link": link,
        "event_date": event_date,
        "event_time": event_time,
    }


def get_announcement(announcement_id, published_only=True):
    """Return one announcement or abort with 404 (also 404 for drafts when published_only)."""
    announcement = db.session.get(Announcement, announcement_id)
    if announcement is None or (published_only and not announcement.is_published):
        abort(404)
    return announcement


def list_for_publisher(author_id):
    return (
        Announcement.query.filter_by(author_id=author_id)
        .order_by(Announcement.created_at.desc(), Announcement.id.desc())
        .all()
    )


def _apply_publish(announcement, published):
    if published:
        if not announcement.is_published:
            announcement.is_published = True
            if announcement.published_at is None:
                announcement.published_at = utcnow()
    else:
        announcement.is_published = False


def _sync_notification(announcement):
    """Published announcements get one notification; drafts must not have any."""
    if announcement.is_published:
        notification_service.notify_published(announcement)
    else:
        notification_service.remove_for(announcement.id)


def create_announcement(data, author_id):
    clean = validate_announcement_data(data)
    announcement = Announcement(author_id=author_id, **clean)
    _apply_publish(announcement, bool(data.get("is_published")))
    db.session.add(announcement)
    db.session.commit()
    _sync_notification(announcement)
    return announcement


def update_announcement(announcement_id, data):
    announcement = get_announcement(announcement_id, published_only=False)
    clean = validate_announcement_data(data)
    for field, value in clean.items():
        setattr(announcement, field, value)
    if "is_published" in data:
        _apply_publish(announcement, bool(data["is_published"]))
    db.session.commit()
    _sync_notification(announcement)
    return announcement


def set_published(announcement_id, published):
    announcement = get_announcement(announcement_id, published_only=False)
    _apply_publish(announcement, published)
    db.session.commit()
    _sync_notification(announcement)
    return announcement


def delete_announcement(announcement_id):
    announcement = get_announcement(announcement_id, published_only=False)
    attachment_service.delete_all_for(announcement_id)  # removes the files on disk too
    db.session.delete(announcement)  # notifications are removed by the cascade
    db.session.commit()
