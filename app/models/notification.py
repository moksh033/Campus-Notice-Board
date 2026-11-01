"""Notification model. Owner: Mridul.

The table is shared by everyone (there are no student accounts). "Read" state is kept
per browser in the Flask session, see services/notification_service.py.
"""
from ..extensions import db, utcnow


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(
        db.Integer, db.ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False
    )
    message = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    announcement = db.relationship("Announcement", back_populates="notifications")
