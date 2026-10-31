# Mihir: Core Application Architecture and Announcement Management

**Branch:** `feature/core-announcement-engine`

## What I own
| File | Purpose |
|---|---|
| `app/__init__.py`, `config.py`, `run.py` | App factory, configuration, entry point |
| `app/extensions.py`, `app/constants.py`, `app/errors.py` | Shared objects, categories and limits, `ValidationError` and error pages |
| `app/models/announcement.py`, `app/models/__init__.py` | Central Announcement model |
| `app/services/announcement_service.py` | Validation, CRUD, publish status |
| `app/forms/announcement_forms.py`, `app/routes/announcements.py` | Admin CRUD pages and the JSON API |
| `app/templates/admin/*`, `app/static/css/admin.css` | Publisher management screens |
| `conftest.py`, `pytest.ini`, `docs/api.md`, `docs/database.md` | Test setup and documentation |

## Tests
`members/mihir/tests/` (`test_app_core.py`, `test_announcement_service.py`, `test_api.py`). Run: `python -m pytest members/mihir`.

## How it connects to the others
Aariz's `@login_required` protects my admin routes. Nayeem's attachment service is called when I save a form and when I delete.
Mridul's `notify_published` is called when an announcement is published. Moksh's dashboard reads announcements through Mridul's search service.
See [implementation.md](implementation.md), [architecture.md](architecture.md) and [api-documentation.md](api-documentation.md).
