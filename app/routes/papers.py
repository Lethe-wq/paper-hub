import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_from_directory,
    current_app,
)
from app import db
from app.models import Paper, Comment
from app.services.pdf_parser import (
    allowed_file,
    extract_text_from_pdf,
    parse_metadata,
    generate_thumbnail,
    save_upload_file,
)

papers_bp = Blueprint("papers", __name__)


@papers_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    tag = request.args.get("tag", "")
    sort = request.args.get("sort", "newest")

    query = Paper.query

    if tag:
        query = query.filter(Paper.tags.contains(tag))

    if sort == "oldest":
        query = query.order_by(Paper.created_at.asc())
    elif sort == "title":
        query = query.order_by(Paper.title.asc())
    else:
        query = query.order_by(Paper.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    papers = pagination.items

    all_tags = set()
    for p in Paper.query.all():
        for t in p.tag_list():
            all_tags.add(t)

    return render_template(
        "index.html",
        papers=papers,
        pagination=pagination,
        tags=sorted(all_tags),
        current_tag=tag,
        sort=sort,
    )


@papers_bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        authors = request.form.get("authors", "").strip()
        year = request.form.get("year", type=int)
        abstract = request.form.get("abstract", "").strip()
        tags = request.form.get("tags", "").strip()

        if "file" not in request.files:
            flash("请选择要上传的PDF文件", "error")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("请选择要上传的PDF文件", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("只支持PDF格式文件", "error")
            return redirect(request.url)

        unique_name, filepath, original_name = save_upload_file(
            file, current_app.config["UPLOAD_FOLDER"]
        )

        thumbnail = generate_thumbnail(
            filepath, current_app.config["THUMBNAIL_FOLDER"]
        )

        paper = Paper(
            title=title or original_name,
            authors=authors,
            year=year or None,
            abstract=abstract,
            filename=original_name,
            filepath=unique_name,
            file_size=os.path.getsize(filepath),
            thumbnail=thumbnail,
            tags=tags,
        )
        db.session.add(paper)
        db.session.commit()

        flash("论文上传成功！", "success")
        return redirect(url_for("papers.detail", paper_id=paper.id))

    return render_template("upload.html")


@papers_bp.route("/upload/parse", methods=["POST"])
def parse_pdf():
    if "file" not in request.files:
        return jsonify({"error": "未找到文件"}), 400

    file = request.files["file"]
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "只支持PDF格式"}), 400

    _, filepath, _ = save_upload_file(file, current_app.config["UPLOAD_FOLDER"])
    text = extract_text_from_pdf(filepath)
    metadata = parse_metadata(text)

    os.remove(filepath)

    return jsonify(metadata)


@papers_bp.route("/paper/<int:paper_id>")
def detail(paper_id):
    paper = Paper.query.get_or_404(paper_id)
    comments = paper.comments.order_by(Comment.created_at.desc()).all()
    return render_template("detail.html", paper=paper, comments=comments)


@papers_bp.route("/paper/<int:paper_id>/edit", methods=["GET", "POST"])
def edit(paper_id):
    paper = Paper.query.get_or_404(paper_id)

    if request.method == "POST":
        paper.title = request.form.get("title", paper.title).strip()
        paper.authors = request.form.get("authors", paper.authors).strip()
        paper.year = request.form.get("year", type=int) or paper.year
        paper.abstract = request.form.get("abstract", paper.abstract).strip()
        paper.tags = request.form.get("tags", paper.tags).strip()
        db.session.commit()

        flash("论文信息已更新", "success")
        return redirect(url_for("papers.detail", paper_id=paper.id))

    return render_template("edit.html", paper=paper)


@papers_bp.route("/paper/<int:paper_id>/delete", methods=["POST"])
def delete(paper_id):
    paper = Paper.query.get_or_404(paper_id)

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], paper.filepath)
    if os.path.exists(filepath):
        os.remove(filepath)

    if paper.thumbnail:
        thumb_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], paper.thumbnail
        )
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

    db.session.delete(paper)
    db.session.commit()

    flash("论文已删除", "success")
    return redirect(url_for("papers.index"))


@papers_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    if not q:
        return render_template("search.html", papers=[], q="", pagination=None)

    query = Paper.query.filter(
        db.or_(
            Paper.title.contains(q),
            Paper.authors.contains(q),
            Paper.abstract.contains(q),
            Paper.tags.contains(q),
        )
    ).order_by(Paper.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    papers = pagination.items

    return render_template("search.html", papers=papers, q=q, pagination=pagination)


@papers_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
