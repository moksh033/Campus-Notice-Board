"""Application factory. Owner: Mihir."""
import os

from flask import Flask

from config import Config

from .extensions import csrf, db, login_manager


def create_app(config_class=None):
    app = Flask(__name__, instance_path=Config.INSTANCE_DIR)
    app.config.from_object(config_class or Config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401  (registers every table with SQLAlchemy)
    from .cli import register_cli
    from .errors import register_error_handlers
    from .routes import register_blueprints
    from .templating import register_template_helpers

    register_blueprints(app)
    register_error_handlers(app)
    register_template_helpers(app)
    register_cli(app)

    with app.app_context():
        db.create_all()

    return app
