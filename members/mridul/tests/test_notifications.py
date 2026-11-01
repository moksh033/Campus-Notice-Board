"""Mridul: database-backed notifications with per-browser read state."""
from app.extensions import db
from app.models import Notification
from app.services import announcement_service as svc


def count(app):
    with app.app_context():
        return Notification.query.count()


def test_publishing_creates_a_stored_notification(app, make_announcement):
    make_announcement("Exam schedule", category="Examinations")
    with app.app_context():
        n = Notification.query.one()
        assert n.message == "New in Examinations: Exam schedule" and n.created_at is not None


def test_drafts_do_not_create_notifications(app, make_announcement):
    make_announcement(published=False)
    assert count(app) == 0


def test_publishing_later_creates_one_notification_only_once(app, make_announcement):
    a_id = make_announcement(published=False)
    with app.app_context():
        svc.set_published(a_id, True)
        svc.update_announcement(a_id, {"title": "Edited", "description": "d", "category": "Events"})
    assert count(app) == 1


def test_unpublishing_removes_the_notification(app, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        svc.set_published(a_id, False)
    assert count(app) == 0


def test_deleting_an_announcement_removes_its_notification(app, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        svc.delete_announcement(a_id)
    assert count(app) == 0


def test_bell_shows_unread_count_and_links_to_the_notice(client, make_announcement):
    a_id = make_announcement("Convocation")
    html = client.get("/").get_data(as_text=True)
    assert 'data-bell-count >1</span>' in html
    assert "New in Examinations: Convocation" in html and f"/notices/{a_id}" in html


def test_empty_bell_message(client):
    assert b"No notifications yet" in client.get("/").data


def test_mark_read_lowers_unread_count_and_is_remembered(client, make_announcement):
    make_announcement("One")
    make_announcement("Two")
    assert client.get("/api/notifications").get_json()["unread"] == 2
    first_id = client.get("/api/notifications").get_json()["notifications"][0]["id"]
    assert client.post(f"/api/notifications/{first_id}/read").get_json()["unread"] == 1
    data = client.get("/api/notifications").get_json()
    assert data["unread"] == 1 and data["notifications"][0]["is_read"] is True


def test_read_state_is_per_browser(app, client, make_announcement):
    make_announcement("Shared")
    nid = client.get("/api/notifications").get_json()["notifications"][0]["id"]
    client.post(f"/api/notifications/{nid}/read")
    other_browser = app.test_client()
    assert other_browser.get("/api/notifications").get_json()["unread"] == 1


def test_mark_all_read(client, make_announcement):
    for name in ("A", "B", "C"):
        make_announcement(name)
    assert client.post("/api/notifications/read-all").get_json()["unread"] == 0
    assert client.get("/api/notifications").get_json()["unread"] == 0


def test_marking_unknown_notification_is_404(client):
    assert client.post("/api/notifications/999/read").status_code == 404


def test_notifications_are_newest_first_and_limited_to_ten(client, make_announcement):
    for i in range(12):
        make_announcement(f"N{i:02d}")
    items = client.get("/api/notifications").get_json()["notifications"]
    assert len(items) == 10 and items[0]["message"].endswith("N11")
