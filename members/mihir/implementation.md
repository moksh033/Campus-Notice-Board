# Implementation notes (Mihir)

- **App factory:** `create_app()` loads config, creates the `instance/` and upload folders, attaches `db`, `login_manager` and `csrf`, registers blueprints, error handlers, template filters and CLI commands, then runs `db.create_all()`.
- **Announcement model:** one table with the fields in `docs/database.md`. A database CHECK constraint limits `category` to the four values. `published_at` is set the first time an announcement is published.
- **Validation:** `validate_announcement_data()` trims text, checks title/description/category, venue length, `http(s)` links and date/time formats, then raises `ValidationError({field: message})`. The form does CSRF and parsing; this function holds the real rules, so the admin pages and tests share one set.
- **CRUD:** `create_announcement`, `update_announcement`, `set_published`, `delete_announcement`, `get_announcement` (404 for drafts unless `published_only=False`), `list_for_publisher`.
- **Publication status:** `is_published` plus `published_at`. After each change `_sync_notification` creates the notification for published items and removes it for drafts.
- **Reliable persistence:** every change commits immediately; SQLite foreign keys are enabled per connection so cascades work.
- **Error handling:** `ValidationError` becomes JSON 400 on API routes; 403/404/413/500 render `errors/error.html` or JSON for `/api/` paths.
- **Ownership:** a publisher can edit, delete or publish only announcements they wrote (403 otherwise).
