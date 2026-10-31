"""Shared error handling. Owner: Mihir."""
from flask import jsonify, render_template, request

from .extensions import db


class ValidationError(Exception):
    """Raised by services when input is invalid.

    `errors` is a dict of {field_name: message}. A plain string is stored under "form".
    """

    def __init__(self, errors):
        if isinstance(errors, str):
            errors = {"form": errors}
        self.errors = errors
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))


def _wants_json():
    return request.path.startswith("/api/")


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify(errors=err.errors), 400

    def make_handler(code, title, message):
        def handler(_err):
            if code == 500:
                db.session.rollback()
            if _wants_json():
                return jsonify(error=message), code
            return render_template("errors/error.html", code=code, title=title, message=message), code

        return handler

    for code, title, message in (
        (403, "Not allowed", "You don't have permission to do that."),
        (404, "Page not found", "We couldn't find that page. It may have been removed or never published."),
        (413, "File too large", "That upload is too large. Posters can be up to 3 MB and PDFs up to 5 MB."),
        (500, "Something went wrong", "An unexpected error occurred. Please try again in a moment."),
    ):
        app.register_error_handler(code, make_handler(code, title, message))
