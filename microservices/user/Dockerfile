FROM python:3.11.9-slim-bookworm AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.11.9-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
EXPOSE 5002
RUN useradd -u 10001 -m appuser
USER 10001
CMD ["python", "app.py"]


