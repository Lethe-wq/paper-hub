# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

大创团队论文管理系统 (Paper Management System) — a Flask web app for a university innovation team to upload, browse, search, and comment on research papers. Deployed on a Tencent Cloud lightweight server (2-core 2GB) via Docker. Chinese-only UI. No authentication system.

## Commands

```bash
# Install dependencies (use Tsinghua mirror in China)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Run dev server
python run.py
# → http://127.0.0.1:5000

# Docker production deployment
docker compose up -d --build
docker compose logs -f        # view logs
docker compose down            # stop

# Redeploy after code changes
git pull && docker compose up -d --build
```

## Architecture

**Flask app factory pattern**: `app/__init__.py` creates the app, initializes SQLAlchemy, registers two blueprints (`papers_bp`, `comments_bp`), and auto-creates DB tables on startup.

**Data flow for paper upload**: User drops PDF → AJAX POST to `/upload/parse` (temp save → PyMuPDF extract text → heuristic metadata parse → delete temp file → return JSON) → form auto-fills → user submits → POST `/upload` (save file, generate thumbnail via PyMuPDF+Pillow, create Paper record).

**File storage**: PDFs are saved with UUID filenames in `uploads/`. Thumbnails rendered from first page at 1.5x scale into `uploads/thumbnails/`. The `uploaded_file` route serves both with `Content-Disposition: inline` for browser viewing.

**PDF inline viewer** (detail.html): Uses PDF.js v3.11.174 loaded from CDN. PDFs are fetched via main-thread `fetch()` as ArrayBuffer, then passed to `pdfjsLib.getDocument({data})` — this bypasses Worker network requests which get blocked by some browser extensions (ERR_BLOCKED_BY_CLIENT). Two view modes: single-page canvas and scrollable all-pages.

**Frontend**: Tailwind CSS (CDN) + Alpine.js. Dark/light theme via Tailwind `dark:` class strategy, toggled by JS and persisted in localStorage. No build step needed.

**Database**: SQLite (`papers.db`) with two models — `Paper` and `Comment` (cascade delete). Tags stored as comma-separated strings, split by `tag_list()` helper. Search uses SQLAlchemy `contains()` (SQL LIKE).

## Key Design Decisions

- No Node.js build step — all frontend deps loaded from CDN (Tailwind, Alpine.js, PDF.js)
- UUID file naming prevents upload conflicts without requiring user management
- PDF.js loads PDF data in-memory to avoid Worker fetch issues on deployed servers
- Dockerfile uses Chinese mirrors (USTC for apt, Tsinghua for pip) for fast builds from China
- `SECRET_KEY` defaults to a dev value; override via environment variable in production

## Config

All config in `app/config.py`. Upload limit: 50MB. Key paths:
- `UPLOAD_FOLDER` = `uploads/`
- `THUMBNAIL_FOLDER` = `uploads/thumbnails/`
- DB = `papers.db` (root directory)
