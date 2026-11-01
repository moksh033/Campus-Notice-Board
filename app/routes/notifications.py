"""Notification bell data and mark-as-read endpoints. Owner: Mridul."""
from flask import Blueprint, jsonify, url_for
from sqlalchemy.exc import SQLAlchemyError

from ..services import notification_service

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


def _as_dicts():
    read = notification_service.read_ids()
    return [
        {
            "id": n.id,
            "announcement_id": n.announcement_id,
            "message": n.message,
            "created_at": n.created_at,
            "is_read": n.id in read,
        }
        for n in notification_service.list_recent()
    ]


@bp.app_context_processor
def inject_notifications():
    """Makes the bell's data available to every template."""
    try:
        items = _as_dicts()
    except SQLAlchemyError:
        items = []
    return {
        "bell_notifications": items,
        "notification_unread_count": sum(1 for i in items if not i["is_read"]),
    }


@bp.get("")
def list_json():
    items = _as_dicts()
    return jsonify(
        unread=sum(1 for i in items if not i["is_read"]),
        notifications=[
            {
                "id": i["id"],
                "message": i["message"],
                "created_at": i["created_at"].isoformat(),
                "is_read": i["is_read"],
                "url": url_for("notices.detail", announcement_id=i["announcement_id"]),
            }
            for i in items
        ],
    )


@bp.post("/<int:notification_id>/read")
def mark_read(notification_id):
    notification_service.mark_read(notification_id)
    return jsonify(ok=True, unread=notification_service.unread_count())


@bp.post("/read-all")
def mark_all_read():
    notification_service.mark_all_read()
    return jsonify(ok=True, unread=0)
