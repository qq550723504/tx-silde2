# 使用官方的 Python 镜像作为基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 清理缓存
RUN rm -rf /root/.cache/pip

# 复制项目代码到容器中
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露端口
EXPOSE 5000

# 启动 Flask 应用
CMD ["flask", "run"]
