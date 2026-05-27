"""数据集相关路由：列表、上传、详情、编辑、删除、搜索、下载"""

import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app,
)
from app import db
from app.models import Dataset
from app.services.pdf_parser import save_upload_file
from app.services.dataset_parser import get_preview_data, is_previewable

datasets_bp = Blueprint("datasets", __name__, url_prefix="/datasets")


@datasets_bp.route("/")
def index():
    """数据集列表页：卡片网格展示，支持标签筛选和排序"""
    page = request.args.get("page", 1, type=int)
    tag = request.args.get("tag", "")
    sort = request.args.get("sort", "newest")

    query = Dataset.query

    if tag:
        query = query.filter(Dataset.tags.contains(tag))

    if sort == "oldest":
        query = query.order_by(Dataset.created_at.asc())
    elif sort == "name":
        query = query.order_by(Dataset.name.asc())
    else:
        query = query.order_by(Dataset.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    datasets = pagination.items

    all_tags = set()
    for d in Dataset.query.all():
        for t in d.tag_list():
            all_tags.add(t)

    return render_template(
        "datasets/index.html",
        datasets=datasets,
        pagination=pagination,
        tags=sorted(all_tags),
        current_tag=tag,
        sort=sort,
    )


@datasets_bp.route("/upload", methods=["GET", "POST"])
def upload():
    """数据集上传：接收表单数据和文件，保存并创建数据库记录"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        tags = request.form.get("tags", "").strip()

        if "file" not in request.files:
            flash("请选择要上传的文件", "error")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("请选择要上传的文件", "error")
            return redirect(request.url)

        # 保存文件到 datasets 目录（UUID 重命名防冲突）
        unique_name, filepath, original_name = save_upload_file(
            file, current_app.config["DATASET_FOLDER"]
        )

        # 提取文件扩展名
        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""

        dataset = Dataset(
            name=name or original_name,
            description=description,
            filename=original_name,
            filepath=unique_name,
            file_size=os.path.getsize(filepath),
            file_type=ext,
            tags=tags,
        )
        db.session.add(dataset)
        db.session.commit()

        flash("数据集上传成功！", "success")
        return redirect(url_for("datasets.detail", dataset_id=dataset.id))

    return render_template("datasets/upload.html")


@datasets_bp.route("/<int:dataset_id>")
def detail(dataset_id):
    """数据集详情页：展示元信息、文件预览、下载按钮"""
    dataset = Dataset.query.get_or_404(dataset_id)

    # 尝试获取预览数据
    preview = None
    if dataset.file_type and is_previewable(dataset.file_type):
        filepath = os.path.join(
            current_app.config["DATASET_FOLDER"], dataset.filepath
        )
        if os.path.exists(filepath):
            preview = get_preview_data(filepath, dataset.file_type)

    return render_template(
        "datasets/detail.html", dataset=dataset, preview=preview
    )


@datasets_bp.route("/<int:dataset_id>/edit", methods=["GET", "POST"])
def edit(dataset_id):
    """编辑数据集元信息"""
    dataset = Dataset.query.get_or_404(dataset_id)

    if request.method == "POST":
        dataset.name = request.form.get("name", dataset.name).strip()
        dataset.description = request.form.get(
            "description", dataset.description
        ).strip()
        dataset.tags = request.form.get("tags", dataset.tags).strip()
        db.session.commit()

        flash("数据集信息已更新", "success")
        return redirect(url_for("datasets.detail", dataset_id=dataset.id))

    return render_template("datasets/edit.html", dataset=dataset)


@datasets_bp.route("/<int:dataset_id>/delete", methods=["POST"])
def delete(dataset_id):
    """删除数据集及其文件"""
    dataset = Dataset.query.get_or_404(dataset_id)

    filepath = os.path.join(
        current_app.config["DATASET_FOLDER"], dataset.filepath
    )
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(dataset)
    db.session.commit()

    flash("数据集已删除", "success")
    return redirect(url_for("datasets.index"))


@datasets_bp.route("/search")
def search():
    """搜索数据集：按名称、描述、标签模糊匹配"""
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    if not q:
        return render_template("datasets/search.html", datasets=[], q="", pagination=None)

    query = Dataset.query.filter(
        db.or_(
            Dataset.name.contains(q),
            Dataset.description.contains(q),
            Dataset.tags.contains(q),
        )
    ).order_by(Dataset.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    datasets = pagination.items

    return render_template("datasets/search.html", datasets=datasets, q=q, pagination=pagination)


@datasets_bp.route("/files/<path:filename>")
def download_file(filename):
    """数据集文件下载"""
    filepath = os.path.join(current_app.config["DATASET_FOLDER"], filename)
    directory = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    response = send_from_directory(directory, basename)
    response.headers["Content-Disposition"] = f"attachment; filename=\"{basename}\""
    return response
