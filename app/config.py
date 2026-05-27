"""应用配置文件"""

import os

# 项目根目录（run.py 所在目录）
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    # Flask 密钥，用于 session 签名等安全功能，生产环境务必通过环境变量设置
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    # SQLite 数据库路径，支持通过 DATABASE_URL 环境变量切换为其他数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'papers.db')}"
    )
    # 关闭 SQLAlchemy 的事件追踪以节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # PDF 文件存储目录
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    # PDF 首页缩略图存储目录
    THUMBNAIL_FOLDER = os.path.join(BASE_DIR, "uploads", "thumbnails")
    # 数据集文件存储目录
    DATASET_FOLDER = os.path.join(BASE_DIR, "uploads", "datasets")
    # 上传文件大小上限：50MB
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
