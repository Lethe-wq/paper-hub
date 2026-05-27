"""数据集解析服务：CSV/JSON 文件预览"""

import csv
import json


# 支持在线预览的文件类型
PREVIEWABLE_EXTENSIONS = {"csv", "json", "tsv"}


def is_previewable(file_type):
    """判断文件类型是否支持在线预览"""
    return file_type.lower() in PREVIEWABLE_EXTENSIONS


def get_preview_data(filepath, file_type, max_rows=20):
    """
    根据文件类型调用对应的预览解析函数。
    返回 dict，包含预览数据；不支持预览的格式返回 None。
    """
    ft = file_type.lower()
    if ft == "csv":
        return preview_csv(filepath, max_rows)
    elif ft == "tsv":
        return preview_tsv(filepath, max_rows)
    elif ft == "json":
        return preview_json(filepath, max_rows)
    return None


def preview_csv(filepath, max_rows=20):
    """
    读取 CSV 文件前 N 行，返回表头和行数据。
    自动检测编码（优先 UTF-8，回退 GBK）。
    """
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            with open(filepath, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)
            return {"type": "table", "headers": headers, "rows": rows}
        except (UnicodeDecodeError, csv.Error):
            continue
    return None


def preview_tsv(filepath, max_rows=20):
    """读取 TSV 文件前 N 行"""
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            with open(filepath, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter="\t")
                headers = next(reader, [])
                rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)
            return {"type": "table", "headers": headers, "rows": rows}
        except (UnicodeDecodeError, csv.Error):
            continue
    return None


def preview_json(filepath, max_rows=20):
    """
    读取 JSON 文件并返回结构化预览。
    支持 JSON 数组（截取前 N 条）和 JSON 对象。
    """
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                data = json.load(f)

            if isinstance(data, list):
                items = data[:max_rows]
                # 数组元素为对象时，提取表头
                if items and isinstance(items[0], dict):
                    headers = list(items[0].keys())
                    rows = [[item.get(h, "") for h in headers] for item in items]
                    return {"type": "table", "headers": headers, "rows": rows}
                # 数组元素为简单值
                return {"type": "list", "items": items}
            elif isinstance(data, dict):
                return {"type": "object", "data": data}
            else:
                return {"type": "raw", "value": str(data)}
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None
