"""PDF 解析服务：提取文本、解析元数据、生成缩略图"""

import os
import re
import uuid
import fitz  # PyMuPDF，用于 PDF 文本提取和页面渲染
from PIL import Image


ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    """检查文件扩展名是否为允许的类型"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    """提取 PDF 前两页的文本内容，用于后续元数据解析"""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page_num in range(min(2, len(doc))):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
        return text
    except Exception:
        return ""


def parse_metadata(text):
    """
    从 PDF 提取的文本中启发式解析论文元数据。
    解析策略：
    - 标题：取第一行非空文本
    - 年份：在前10行中查找 1900-2099 的四位数
    - 作者：标题后的第一行
    - 摘要：查找 "Abstract" 关键词，提取其后直到 "Introduction" 等段落标题的内容
    """
    metadata = {"title": "", "authors": "", "year": None, "abstract": ""}

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return metadata

    # 第一行通常为论文标题
    metadata["title"] = lines[0]

    # 在前10行中查找年份（匹配 19xx 或 20xx）
    year_pattern = re.compile(r"\b(19|20)\d{2}\b")
    for i, line in enumerate(lines[:10]):
        match = year_pattern.search(line)
        if match:
            metadata["year"] = int(match.group())
            # 年份出现在第 1-3 行时，第 2 行通常是作者
            if i > 0 and i <= 3:
                metadata["authors"] = lines[1] if len(lines) > 1 else ""
            break

    # 如果前面没有识别到作者，默认取第二行
    if not metadata["authors"] and len(lines) > 1:
        metadata["authors"] = lines[1]

    # 查找 Abstract 段落的起始位置
    abstract_start = -1
    for i, line in enumerate(lines):
        if re.match(r"^abstract", line, re.IGNORECASE):
            abstract_start = i
            break

    # 提取 Abstract 段落内容，直到遇到 Introduction / Keywords 等段落标题
    if abstract_start >= 0:
        abstract_text = lines[abstract_start]
        if len(abstract_text) > len("abstract"):
            abstract_text = abstract_text[len("abstract"):].strip(":—– \n")
        for j in range(abstract_start + 1, min(abstract_start + 15, len(lines))):
            next_line = lines[j]
            if re.match(r"^(introduction|keywords|1[\.\s])", next_line, re.IGNORECASE):
                break
            abstract_text += " " + next_line
        metadata["abstract"] = abstract_text.strip()

    return metadata


def generate_thumbnail(filepath, thumbnail_folder, max_size=(200, 280)):
    """
    将 PDF 首页渲染为 PNG 缩略图。
    使用 PyMuPDF 以 1.5 倍缩放渲染，再用 Pillow 缩放到目标尺寸。
    返回缩略图的相对路径，失败返回空字符串。
    """
    try:
        doc = fitz.open(filepath)
        page = doc[0]
        # 1.5 倍缩放渲染，提高清晰度
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        # 等比缩放到目标尺寸
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # 使用 UUID 作为文件名，避免冲突
        thumb_name = f"{uuid.uuid4().hex}.png"
        thumb_path = os.path.join(thumbnail_folder, thumb_name)
        img.save(thumb_path, "PNG")
        doc.close()
        return f"thumbnails/{thumb_name}"
    except Exception:
        return ""


def save_upload_file(file, upload_folder):
    """
    保存上传的文件到指定目录。
    使用 UUID 重命名文件以避免名称冲突。
    返回：(唯一文件名, 完整路径, 原始文件名)
    """
    original_name = file.filename
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)
    return unique_name, filepath, original_name
