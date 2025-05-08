FROM python:3.12.6-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -e .

# 确保日志目录存在（宿主机会挂载 ./.log 进来）
RUN mkdir -p .log

CMD ["bash", "-c", "python -m dispatch.cli server start --host 0.0.0.0 --port 8000 dispatch.main:app 1>>.log/mes_8000.log 2>&1"]
