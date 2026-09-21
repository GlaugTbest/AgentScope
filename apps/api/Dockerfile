FROM python:3.13-slim
WORKDIR /app
COPY apps/api /app/apps/api
RUN pip install --no-cache-dir "/app/apps/api[postgres]"
WORKDIR /app/apps/api
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "python -m alembic -c alembic.ini upgrade head && python -m uvicorn agentscope_api.main:app --host 0.0.0.0 --port 8000"]
