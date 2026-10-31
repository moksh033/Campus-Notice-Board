"""Announcement create/edit form. Owner: Mihir.

The form handles CSRF and turning the browser's text into Python values.
The real rules (lengths, categories, links) live in announcement_service.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import BooleanField, DateField, SelectField, StringField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Optional

from ..constants import CATEGORIES, LINK_MAX, TITLE_MAX, VENUE_MAX


class AnnouncementForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=TITLE_MAX)])
    description = TextAreaField("Description", validators=[DataRequired()])
    category = SelectField("Category", choices=list(CATEGORIES))
    event_date = DateField("Event date (optional)", validators=[Optional()])
    event_time = TimeField("Event time (optional)", format="%H:%M", validators=[Optional()])
    venue = StringField("Venue (optional)", validators=[Optional(), Length(max=VENUE_MAX)])
    registration_link = StringField(
        "Registration link (optional)", validators=[Optional(), Length(max=LINK_MAX)]
    )
    poster = FileField("Poster image (PNG, JPG or WEBP, up to 3 MB)")
    pdf = FileField("PDF notice (up to 5 MB)")
    remove_poster = BooleanField("Remove current poster")
    remove_pdf = BooleanField("Remove current PDF")
    is_published = BooleanField("Publish now (visible to students)")

    DATA_FIELDS = (
        "title", "description", "category", "event_date", "event_time",
        "venue", "registration_link", "is_published",
    )

    def service_data(self):
        """The fields announcement_service expects."""
        return {name: getattr(self, name).data for name in self.DATA_FIELDS}
