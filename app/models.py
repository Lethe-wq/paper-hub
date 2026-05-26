"""数据模型定义"""

from datetime import datetime, timezone
from app import db


class Paper(db.Model):
    """论文模型，存储论文的元信息和文件路径"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)       # 论文标题
    authors = db.Column(db.String(500), default="")          # 作者，逗号分隔
    year = db.Column(db.Integer, nullable=True)              # 发表年份
    abstract = db.Column(db.Text, default="")                # 摘要
    filename = db.Column(db.String(200), nullable=False)     # 用户上传时的原始文件名
    filepath = db.Column(db.String(500), nullable=False)     # 服务器上的唯一存储文件名
    file_size = db.Column(db.Integer, default=0)             # 文件大小（字节）
    thumbnail = db.Column(db.String(500), default="")        # 首页缩略图相对路径
    tags = db.Column(db.String(200), default="")             # 标签，逗号分隔
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    # 关联评论，删除论文时级联删除所有评论
    comments = db.relationship("Comment", backref="paper", lazy="dynamic", cascade="all, delete-orphan")

    def tag_list(self):
        """将逗号分隔的标签字符串转为列表"""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def file_size_display(self):
        """将字节数转为人类可读的大小格式"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class Comment(db.Model):
    """评论模型，团队成员对论文的评论和笔记"""
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey("paper.id"), nullable=False)  # 所属论文
    author_name = db.Column(db.String(100), nullable=False)  # 评论者名字
    content = db.Column(db.Text, nullable=False)             # 评论内容
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
