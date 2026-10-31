# Database (SQLite via Flask-SQLAlchemy)

The file is `instance/campusconnect.db`. Tables are created automatically when the app starts.

```text
publishers 1 ──< announcements 1 ──< attachments   (max 1 poster + 1 PDF)
                              1 ──< notifications
```

**publishers** (Aariz): `id`, `username` (unique), `email` (unique), `password_hash`, `created_at`.

**announcements** (Mihir): `id`, `title` (150), `description`, `category` (CHECK: one of the 4),
`author_id` -> publishers, `created_at`, `updated_at`, `published_at` (set on first publish),
`event_date`, `event_time`, `venue`, `registration_link`, `is_published`.
Index on `(is_published, published_at)`.

**attachments** (Nayeem): `id`, `announcement_id` -> announcements (cascade), `kind` (`poster`/`pdf`),
`stored_filename` (random name on disk), `original_filename`, `mime_type`, `size_bytes`, `uploaded_at`.
`UNIQUE(announcement_id, kind)`.

**notifications** (Mridul): `id`, `announcement_id` -> announcements (cascade), `message`, `created_at`.
Read state is not a column: see "Design decisions" in the README.

Deleting an announcement removes its attachments (rows and files) and notifications.
SQLite foreign keys are switched on for every connection in `app/extensions.py`.
To reset everything during development, stop the app and delete the `instance/` folder.
