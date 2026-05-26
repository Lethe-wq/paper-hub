# 论文管理系统

大创团队内部使用的论文管理平台，支持 PDF 上传、自动解析元数据、分类标签、搜索、评论等功能。

## 功能

- **论文上传**：拖拽上传 PDF，自动解析标题、作者、摘要等信息，支持手动修正
- **论文浏览**：卡片式列表展示，含 PDF 首页缩略图
- **分类标签**：自定义标签，按研究方向筛选
- **全文搜索**：按标题、作者、摘要、标签模糊搜索
- **评论笔记**：团队成员可对论文发表评论和笔记
- **主题切换**：亮色 / 暗色主题
- **PDF 预览**：在线预览或下载原文

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Flask + SQLAlchemy |
| 数据库 | SQLite |
| PDF 解析 | PyMuPDF |
| 前端 | Tailwind CSS + Alpine.js |
| 部署 | Docker + Gunicorn |

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动
python run.py
```

访问 http://127.0.0.1:5000

## Docker 部署

```bash
# 构建并启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

服务启动后访问 `http://服务器IP:5000`。

> 部署前需在腾讯云防火墙中开放 5000 端口（TCP）。

## 数据存储

- `papers.db` — SQLite 数据库文件
- `uploads/` — PDF 原文
- `uploads/thumbnails/` — 首页缩略图

以上目录通过 Docker volumes 挂载到宿主机，容器重建不丢失数据。

## 项目结构

```
app/
├── __init__.py          # 应用工厂
├── config.py            # 配置
├── models.py            # 数据模型
├── routes/
│   ├── papers.py        # 论文路由
│   └── comments.py      # 评论路由
├── services/
│   └── pdf_parser.py    # PDF 解析与缩略图生成
├── templates/           # 页面模板
└── static/              # 静态资源
```
