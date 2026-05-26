import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["THUMBNAIL_FOLDER"], exist_ok=True)

    from app.routes.papers import papers_bp
    from app.routes.comments import comments_bp

    app.register_blueprint(papers_bp)
    app.register_blueprint(comments_bp)

    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
