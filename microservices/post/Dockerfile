FROM python:3.11.9-slim-bookworm AS builder
WORKDIR /app

# Instala solo lo necesario para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Usa wheels para acelerar instalación en etapa final
COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels -r requirements.txt

# Etapa 2: Imagen final
FROM python:3.11.9-slim-bookworm
WORKDIR /app

# Instalar certificados SSL
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copia dependencias precompiladas y las instala
COPY --from=builder /wheels /wheels
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt
COPY . .

ENV PYTHONPATH=/app
EXPOSE 5003

# Crear usuario no root
RUN useradd -u 10001 -m appuser
USER 10001

CMD ["python", "app.py"]