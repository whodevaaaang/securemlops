# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home /app app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY api ./api
COPY model ./model

RUN python -m model.train \
    && chown -R app:app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=3).status==200 else 1)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
