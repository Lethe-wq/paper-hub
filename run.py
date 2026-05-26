"""应用启动入口"""

from app import create_app

# 创建 Flask 应用实例
app = create_app()

if __name__ == "__main__":
    # 开发模式：监听所有网络接口，端口 5000
    # 生产环境请使用 gunicorn（见 Dockerfile）
    app.run(host="0.0.0.0", port=5000, debug=True)
