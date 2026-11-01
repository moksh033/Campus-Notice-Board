"""Search and category filtering. Owner: Mridul."""
from sqlalchemy import or_

from ..constants import CATEGORIES
from ..models import Announcement


def _escape_like(text):
    """Make %, _ and \\ in the user's text match literally."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_announcements(q=None, category=None, page=1, per_page=9):
    """Published announcements, newest first, optionally filtered by keyword and category."""
    query = Announcement.published_query()

    if category in CATEGORIES:
        query = query.filter(Announcement.category == category)

    keyword = (q or "").strip()
    if keyword:
        pattern = f"%{_escape_like(keyword)}%"
        query = query.filter(
            or_(
                Announcement.title.ilike(pattern, escape="\\"),
                Announcement.description.ilike(pattern, escape="\\"),
                Announcement.venue.ilike(pattern, escape="\\"),
            )
        )

    query = query.order_by(Announcement.published_at.desc(), Announcement.id.desc())
    return query.paginate(page=max(page, 1), per_page=per_page, error_out=False)
