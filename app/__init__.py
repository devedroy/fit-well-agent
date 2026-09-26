"""
Flask application factory.
"""

from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object("app.config.Config")

    from app.routes import bp
    app.register_blueprint(bp)

    return app

