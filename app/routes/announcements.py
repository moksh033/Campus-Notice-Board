"""Publisher management pages (admin) and the read-only JSON API. Owner: Mihir."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import CATEGORIES
from ..errors import ValidationError
from ..forms.announcement_forms import AnnouncementForm
from ..services import announcement_service, attachment_service, search_service

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
api_bp = Blueprint("api", __name__, url_prefix="/api")


# ---------------------------------------------------------------- admin pages

def _own_announcement(announcement_id):
    """Load an announcement and make sure the logged-in publisher wrote it."""
    announcement = announcement_service.get_announcement(announcement_id, published_only=False)
    if announcement.author_id != current_user.id:
        abort(403)
    return announcement


def _save_form(form, announcement=None):
    """Validate files, save the announcement, then save/remove attachments."""
    uploads = {"poster": form.poster.data, "pdf": form.pdf.data}
    uploads = {kind: f for kind, f in uploads.items() if f and f.filename}
    for kind, f in uploads.items():
        attachment_service.check_file(kind, f)  # fail before anything is saved

    data = form.service_data()
    if announcement is None:
        saved = announcement_service.create_announcement(data, current_user.id)
    else:
        saved = announcement_service.update_announcement(announcement.id, data)

    for kind, f in uploads.items():
        attachment_service.save_attachment(saved.id, kind, f)
    for kind in attachment_service.KINDS:
        if getattr(form, f"remove_{kind}").data and kind not in uploads:
            attachment_service.delete_attachment(saved.id, kind)
    return saved


@admin_bp.get("/")
@login_required
def dashboard():
    announcements = announcement_service.list_for_publisher(current_user.id)
    return render_template("admin/dashboard.html", announcements=announcements)


@admin_bp.route("/announcements/new", methods=["GET", "POST"])
@login_required
def create():
    form = AnnouncementForm()
    errors = {}
    if form.validate_on_submit():
        try:
            saved = _save_form(form)
        except ValidationError as err:
            errors = err.errors
        else:
            flash("Announcement saved." + (" It is now live." if saved.is_published else " It is saved as a draft."), "success")
            return redirect(url_for("admin.dashboard"))
    status = 400 if (errors or form.errors) else 200
    return render_template("admin/announcement_form.html", form=form, errors=errors, announcement=None), status


@admin_bp.route("/announcements/<int:announcement_id>/edit", methods=["GET", "POST"])
@login_required
def edit(announcement_id):
    announcement = _own_announcement(announcement_id)
    form = AnnouncementForm(obj=announcement)
    errors = {}
    if form.validate_on_submit():
        try:
            _save_form(form, announcement)
        except ValidationError as err:
            errors = err.errors
        else:
            flash("Changes saved.", "success")
            return redirect(url_for("admin.dashboard"))
    status = 400 if (errors or form.errors) else 200
    return render_template("admin/announcement_form.html", form=form, errors=errors, announcement=announcement), status


@admin_bp.post("/announcements/<int:announcement_id>/delete")
@login_required
def delete(announcement_id):
    _own_announcement(announcement_id)
    announcement_service.delete_announcement(announcement_id)
    flash("Announcement deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/announcements/<int:announcement_id>/publish")
@login_required
def toggle_publish(announcement_id):
    announcement = _own_announcement(announcement_id)
    updated = announcement_service.set_published(announcement_id, not announcement.is_published)
    flash("Announcement published." if updated.is_published else "Announcement unpublished. Students can no longer see it.", "success")
    return redirect(url_for("admin.dashboard"))


# ------------------------------------------------------------------ JSON API

@api_bp.get("/announcements")
def list_announcements():
    category = request.args.get("category", "").strip() or None
    if category and category not in CATEGORIES:
        raise ValidationError({"category": "Category must be one of: " + ", ".join(CATEGORIES) + "."})
    page = request.args.get("page", 1, type=int)
    pagination = search_service.search_announcements(
        request.args.get("q"), category, page=page, per_page=9
    )
    return jsonify(
        items=[a.to_dict() for a in pagination.items],
        page=pagination.page,
        pages=pagination.pages,
        total=pagination.total,
    )


@api_bp.get("/announcements/<int:announcement_id>")
def get_announcement(announcement_id):
    return jsonify(announcement_service.get_announcement(announcement_id).to_dict())
