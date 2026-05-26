from flask import Blueprint, request, redirect, url_for, flash, current_app
from app import db
from app.models import Comment

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/paper/<int:paper_id>/comment", methods=["POST"])
def add(paper_id):
    author_name = request.form.get("author_name", "").strip()
    content = request.form.get("content", "").strip()

    if not author_name or not content:
        flash("请填写名字和评论内容", "error")
        return redirect(url_for("papers.detail", paper_id=paper_id))

    comment = Comment(
        paper_id=paper_id,
        author_name=author_name,
        content=content,
    )
    db.session.add(comment)
    db.session.commit()

    flash("评论已发表", "success")
    return redirect(url_for("papers.detail", paper_id=paper_id))


@comments_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    paper_id = comment.paper_id
    db.session.delete(comment)
    db.session.commit()
    flash("评论已删除", "success")
    return redirect(url_for("papers.detail", paper_id=paper_id))
