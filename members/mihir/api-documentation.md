# API documentation (Mihir)

The full reference is in [`docs/api.md`](../../docs/api.md). My part: `GET /api/announcements` (search, category, page),
`GET /api/announcements/<id>`, and the admin routes `admin.dashboard`, `admin.create`, `admin.edit`, `admin.delete`, `admin.toggle_publish`.
Validation failures return `400 {"errors": {field: message}}`; missing or unpublished items return 404.
