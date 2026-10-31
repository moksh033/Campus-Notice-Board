"""Central Announcement model. Owner: Mihir."""
from sqlalchemy import CheckConstraint, Index

from ..constants import CATEGORIES
from ..extensions import db, utcnow

_CATEGORY_SQL = ", ".join(f"'{c}'" for c in CATEGORIES)


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("publishers.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    published_at = db.Column(db.DateTime)  # set the first time it is published
    event_date = db.Column(db.Date)
    event_time = db.Column(db.Time)
    venue = db.Column(db.String(150))
    registration_link = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    author = db.relationship("Publisher", back_populates="announcements")
    attachments = db.relationship(
        "Attachment", back_populates="announcement", cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", back_populates="announcement", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(f"category IN ({_CATEGORY_SQL})", name="ck_announcement_category"),
        Index("ix_announcement_published", "is_published", "published_at"),
    )

    @classmethod
    def published_query(cls):
        """Base query for everything students are allowed to see."""
        return cls.query.filter(cls.is_published.is_(True))

    def get_attachment(self, kind):
        for attachment in self.attachments:
            if attachment.kind == kind:
                return attachment
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "event_time": self.event_time.strftime("%H:%M") if self.event_time else None,
            "venue": self.venue,
            "registration_link": self.registration_link,
            "has_poster": self.get_attachment("poster") is not None,
            "has_pdf": self.get_attachment("pdf") is not None,
        }
