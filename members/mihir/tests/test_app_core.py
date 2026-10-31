"""Mihir: application startup, database connectivity and error handling."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Announcement


def test_app_starts_and_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_database_is_connected(app):
    with app.app_context():
        assert db.session.execute(text("SELECT 1")).scalar() == 1


def test_tests_use_a_separate_database(app):
    assert "test.db" in app.config["SQLALCHEMY_DATABASE_URI"]
    assert "campusconnect.db" not in app.config["SQLALCHEMY_DATABASE_URI"]


def test_sqlite_foreign_keys_are_enforced(app):
    with app.app_context():
        assert db.session.execute(text("PRAGMA foreign_keys")).scalar() == 1


def test_database_rejects_unknown_category(app, publisher):
    with app.app_context():
        db.session.add(Announcement(title="x", description="y", category="Sports", author_id=publisher))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_unknown_page_shows_friendly_404(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_unknown_api_route_returns_json_404(client):
    response = client.get("/api/announcements/9999")
    assert response.status_code == 404
    assert response.is_json
