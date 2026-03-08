FROM python:3.12-slim-bookworm
WORKDIR /app

# uv 설치
RUN pip install --no-cache-dir uv

# 의존성 먼저 복사 (캐시 활용)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# 소스 복사
COPY main.py ./
COPY app ./app

# 비권한 사용자
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 54321
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "54321"]
