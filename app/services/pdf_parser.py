import os
import re
import uuid
import fitz  # PyMuPDF
from PIL import Image


ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
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
    metadata = {"title": "", "authors": "", "year": None, "abstract": ""}

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return metadata

    metadata["title"] = lines[0]

    year_pattern = re.compile(r"\b(19|20)\d{2}\b")
    for i, line in enumerate(lines[:10]):
        match = year_pattern.search(line)
        if match:
            metadata["year"] = int(match.group())
            if i > 0 and i <= 3:
                metadata["authors"] = lines[1] if len(lines) > 1 else ""
            break

    if not metadata["authors"] and len(lines) > 1:
        metadata["authors"] = lines[1]

    abstract_start = -1
    for i, line in enumerate(lines):
        if re.match(r"^abstract", line, re.IGNORECASE):
            abstract_start = i
            break

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
    try:
        doc = fitz.open(filepath)
        page = doc[0]
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        thumb_name = f"{uuid.uuid4().hex}.png"
        thumb_path = os.path.join(thumbnail_folder, thumb_name)
        img.save(thumb_path, "PNG")
        doc.close()
        return f"thumbnails/{thumb_name}"
    except Exception:
        return ""


def save_upload_file(file, upload_folder):
    original_name = file.filename
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)
    return unique_name, filepath, original_name
