"""Shared pytest fixtures. Every test gets a fresh app, a fresh SQLite file and a fresh upload folder."""
import io
import re

import pytest

from app import create_app
from app.extensions import db
from app.models import Publisher
from app.services import announcement_service
from config import TestConfig

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
PDF_BYTES = b"%PDF-1.4\n" + b"0" * 64


def _build_app(tmp_path, csrf=False):
    class Cfg(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
        UPLOAD_FOLDER = str(tmp_path / "uploads")
        WTF_CSRF_ENABLED = csrf

    return create_app(Cfg)


def _teardown(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def app(tmp_path):
    app = _build_app(tmp_path)
    yield app
    _teardown(app)


@pytest.fixture
def csrf_app(tmp_path):
    """Same app, but with CSRF protection switched on (as in production)."""
    app = _build_app(tmp_path, csrf=True)
    yield app
    _teardown(app)


@pytest.fixture
def client(app):
    return app.test_client()


def create_publisher(app, username="editor", password="password123"):
    with app.app_context():
        publisher = Publisher(username=username, email=f"{username}@example.com")
        publisher.set_password(password)
        db.session.add(publisher)
        db.session.commit()
        return publisher.id


@pytest.fixture
def publisher(app):
    return create_publisher(app, "editor")


@pytest.fixture
def other_publisher(app):
    return create_publisher(app, "other")


@pytest.fixture
def login(client):
    def _login(username="editor", password="password123"):
        return client.post("/auth/login", data={"username": username, "password": password})

    return _login


@pytest.fixture
def logged_in(client, publisher, login):
    login()
    return client


@pytest.fixture
def make_announcement(app, publisher):
    """Create an announcement directly through the service and return its id."""

    def _make(title="Mid-sem timetable", category="Examinations", published=True, author_id=None, **extra):
        data = {
            "title": title,
            "description": f"Full details about {title}.",
            "category": category,
            "is_published": published,
        }
        data.update(extra)
        with app.app_context():
            return announcement_service.create_announcement(data, author_id or publisher).id

    return _make


@pytest.fixture
def png_file():
    return lambda name="poster.png": (io.BytesIO(PNG_BYTES), name)


@pytest.fixture
def pdf_file():
    return lambda name="notice.pdf": (io.BytesIO(PDF_BYTES), name)


def csrf_token_from(html):
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html) or re.search(
        r'value="([^"]+)"[^>]*name="csrf_token"', html
    )
    return match.group(1)


def main_content(html):
    """Only the page body, without the header (which contains the notification bell)."""
    return html.split("<main", 1)[1].split("</main>", 1)[0]
