FROM python:3.13-slim

# 安装 pipx 和 poetry
RUN apt-get update && apt-get install -y pipx
RUN pipx ensurepath
RUN pipx install poetry

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY pyproject.toml ./
RUN pipx run poetry install --no-root

# 复制应用代码
COPY todo todo

# 运行 Flask 应用
CMD ["bash", "-c", "sleep 10 && pipx run poetry run flask --app todo run --host 0.0.0.0 --port 6400"]