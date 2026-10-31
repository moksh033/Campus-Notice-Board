"""Extension objects are created here and attached to the app in create_app()."""
import sqlite3
from datetime import datetime, timezone

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to manage announcements."
login_manager.login_message_category = "error"
login_manager.session_protection = "strong"


def utcnow():
    """Current UTC time as a naive datetime (SQLite stores it without a timezone)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _record):
    """SQLite ignores foreign keys unless this pragma is switched on for each connection."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
