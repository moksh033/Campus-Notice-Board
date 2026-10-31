# API and route reference

Endpoint names are a contract: other modules link with `url_for("<endpoint>")`.

## Public pages (no login)

| Endpoint | URL | Notes |
|---|---|---|
| `dashboard.index` | `GET /?q=&category=&page=` | Published announcements, newest first, 9 per page |
| `notices.detail` | `GET /notices/<announcement_id>` | 404 if missing or unpublished |
| `notices.poster` | `GET /notices/<announcement_id>/poster` | Poster image, 404 if none/missing |
| `notices.pdf` | `GET /notices/<announcement_id>/pdf?download=1` | Inline by default, `download=1` forces download |

## Publisher pages (login required; edit/delete/publish only for the announcement's author, else 403)

| Endpoint | URL | Method |
|---|---|---|
| `auth.login` | `/auth/login?next=` | GET, POST |
| `auth.logout` | `/auth/logout` | POST |
| `admin.dashboard` | `/admin/` | GET |
| `admin.create` | `/admin/announcements/new` | GET, POST (multipart: optional `poster`, `pdf`) |
| `admin.edit` | `/admin/announcements/<announcement_id>/edit` | GET, POST (`remove_poster`, `remove_pdf` checkboxes) |
| `admin.delete` | `/admin/announcements/<announcement_id>/delete` | POST |
| `admin.toggle_publish` | `/admin/announcements/<announcement_id>/publish` | POST |

All POST requests need the CSRF token (`csrf_token` form field, or `X-CSRFToken` header for fetch).

## JSON API

### `GET /api/announcements`
Query: `q` (keyword), `category` (one of the four), `page`.
```json
{"items": [{"id": 1, "title": "...", "description": "...", "category": "Events",
            "published_at": "2026-10-31T09:00:00", "event_date": "2026-12-05",
            "event_time": "14:30", "venue": "...", "registration_link": "https://...",
            "has_poster": true, "has_pdf": false}],
 "page": 1, "pages": 1, "total": 1}
```
An unknown `category` returns `400 {"errors": {"category": "..."}}`.

### `GET /api/announcements/<id>`
One announcement (same fields as above). `404 {"error": "..."}` if missing or unpublished.

### Notifications
| Endpoint | URL | Response |
|---|---|---|
| `notifications.list_json` | `GET /api/notifications` | `{"unread": 2, "notifications": [{"id", "message", "created_at", "is_read", "url"}]}` (latest 10) |
| `notifications.mark_read` | `POST /api/notifications/<id>/read` | `{"ok": true, "unread": 1}`; 404 if unknown |
| `notifications.mark_all_read` | `POST /api/notifications/read-all` | `{"ok": true, "unread": 0}` |

## Service interfaces

```python
# announcement_service (Mihir)
create_announcement(data, author_id) / update_announcement(id, data) / delete_announcement(id)
set_published(id, published) / get_announcement(id, published_only=True) / list_for_publisher(author_id)
validate_announcement_data(data)           # raises app.errors.ValidationError({field: message})
# attachment_service (Nayeem)
check_file(kind, file) / save_attachment(id, kind, file) / delete_attachment(id, kind)
delete_all_for(id) / get_attachment(id, kind) / file_exists(attachment)
# search_service (Mridul)
search_announcements(q, category, page, per_page) -> Pagination
# notification_service (Mridul)
notify_published(a) / remove_for(id) / list_recent() / unread_count() / mark_read(id) / mark_all_read()
```
Integration hooks: publishing calls `notify_published`; unpublishing calls `remove_for`;
deleting an announcement calls `attachment_service.delete_all_for`.

## Limits and rules

- Poster: png, jpg, jpeg, webp, up to 3 MB. PDF: up to 5 MB. File contents are checked against the file type.
- Title up to 150 characters; registration link must start with `http://` or `https://`.
