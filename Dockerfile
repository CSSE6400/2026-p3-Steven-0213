FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .
COPY poetry.lock* .

# 安装 poetry 和依赖
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# 复制应用代码
COPY app/ ./app/
COPY run.py .

# 创建上传目录
RUN mkdir -p /app/uploads /app/instance

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["python", "run.py"]