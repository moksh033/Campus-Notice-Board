"""Mihir: announcement CRUD, category validation and publication status."""
import pytest
from werkzeug.exceptions import NotFound

from app.constants import CATEGORIES
from app.errors import ValidationError
from app.extensions import db
from app.models import Announcement
from app.services import announcement_service as svc


def valid(**over):
    data = {"title": "Hackathon", "description": "48 hour event", "category": "Events"}
    data.update(over)
    return data


def test_create_saves_a_draft_by_default(app, publisher):
    with app.app_context():
        a = svc.create_announcement(valid(), publisher)
        assert a.id and a.is_published is False and a.published_at is None


def test_create_published_sets_published_at(app, publisher):
    with app.app_context():
        a = svc.create_announcement(valid(is_published=True), publisher)
        assert a.is_published and a.published_at is not None


def test_data_persists_in_a_fresh_session(app, publisher):
    with app.app_context():
        a_id = svc.create_announcement(valid(venue="Hall A"), publisher).id
        db.session.remove()
        assert db.session.get(Announcement, a_id).venue == "Hall A"


@pytest.mark.parametrize("category", CATEGORIES)
def test_all_four_categories_are_accepted(app, publisher, category):
    with app.app_context():
        assert svc.create_announcement(valid(category=category), publisher).category == category


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("title", "x" * 151),
        ("description", "   "),
        ("category", "Sports"),
        ("category", ""),
        ("registration_link", "javascript:alert(1)"),
        ("registration_link", "ftp://example.com"),
        ("event_date", "31/12/2026"),
        ("event_time", "25:99"),
    ],
)
def test_invalid_input_is_rejected(app, publisher, field, value):
    with app.app_context():
        with pytest.raises(ValidationError) as excinfo:
            svc.create_announcement(valid(**{field: value}), publisher)
        assert field in excinfo.value.errors
        assert Announcement.query.count() == 0


def test_input_is_trimmed_and_optional_fields_are_stored(app, publisher):
    with app.app_context():
        a = svc.create_announcement(
            valid(title="  Fest  ", event_date="2026-12-05", event_time="10:30",
                  registration_link="https://example.com/r"),
            publisher,
        )
        assert a.title == "Fest"
        assert a.event_date.isoformat() == "2026-12-05"
        assert a.event_time.strftime("%H:%M") == "10:30"


def test_update_changes_fields(app, publisher):
    with app.app_context():
        a_id = svc.create_announcement(valid(), publisher).id
        updated = svc.update_announcement(a_id, valid(title="Hackathon 2.0", category="Clubs"))
        assert (updated.title, updated.category) == ("Hackathon 2.0", "Clubs")


def test_update_with_invalid_data_changes_nothing(app, publisher):
    with app.app_context():
        a_id = svc.create_announcement(valid(), publisher).id
        with pytest.raises(ValidationError):
            svc.update_announcement(a_id, valid(category="Nope"))
        db.session.rollback()
        assert db.session.get(Announcement, a_id).category == "Events"


def test_publish_and_unpublish_keeps_first_published_date(app, publisher):
    with app.app_context():
        a_id = svc.create_announcement(valid(), publisher).id
        first = svc.set_published(a_id, True).published_at
        assert svc.set_published(a_id, False).is_published is False
        again = svc.set_published(a_id, True)
        assert again.is_published and again.published_at == first


def test_delete_removes_the_announcement(app, publisher):
    with app.app_context():
        a_id = svc.create_announcement(valid(), publisher).id
        svc.delete_announcement(a_id)
        assert db.session.get(Announcement, a_id) is None


def test_get_hides_drafts_from_the_public(app, publisher):
    with app.app_context():
        a_id = svc.create_announcement(valid(), publisher).id
        with pytest.raises(NotFound):
            svc.get_announcement(a_id)
        assert svc.get_announcement(a_id, published_only=False).id == a_id


def test_get_missing_announcement_is_404(app):
    with app.app_context():
        with pytest.raises(NotFound):
            svc.get_announcement(12345)


def test_list_for_publisher_only_returns_their_own(app, publisher, other_publisher):
    with app.app_context():
        svc.create_announcement(valid(title="Mine"), publisher)
        svc.create_announcement(valid(title="Theirs"), other_publisher)
        assert [a.title for a in svc.list_for_publisher(publisher)] == ["Mine"]
