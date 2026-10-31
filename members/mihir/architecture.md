# Architecture (Mihir)

One Flask application, built with the factory pattern. Layers: **routes** (HTTP) -> **services** (rules) -> **models** (tables).
Blueprints: `dashboard`, `notices`, `auth`, `admin`, `api`, `notifications`.
Modules use each other's services or models, never routes; links between modules use `url_for("blueprint.endpoint")`.
Integration hooks: publish -> `notification_service.notify_published`; unpublish -> `remove_for`; delete -> `attachment_service.delete_all_for`.
Upload files live in `instance/uploads/`, outside `static/`. See the folder diagram in the main README.
