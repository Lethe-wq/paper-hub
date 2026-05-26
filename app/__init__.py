"""Flask 应用工厂模块"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

# 全局数据库实例，在 create_app() 中初始化
db = SQLAlchemy()


def create_app():
    """创建并配置 Flask 应用实例"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 将数据库绑定到应用
    db.init_app(app)

    # 确保文件上传目录存在
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["THUMBNAIL_FOLDER"], exist_ok=True)

    # 注册路由蓝图
    from app.routes.papers import papers_bp
    from app.routes.comments import comments_bp

    app.register_blueprint(papers_bp)
    app.register_blueprint(comments_bp)

    # 在应用上下文中创建所有数据库表（如果不存在）
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
