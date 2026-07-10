# --- Stage 1 : build des dependances dans un venv isole ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Stage 2 : image finale, minimale ---
FROM python:3.12-slim-bookworm

# Applique les derniers correctifs de securite Debian disponibles pour cette release,
# puis nettoie les caches (reduit la taille + les CVE OS connues au moment du build).
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root (evite l'execution en root dans le conteneur)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# On ne recupere que le venv pret a l'emploi depuis le stage builder :
# pas de compilateur, pas d'outils de build dans l'image finale.
COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/

ENV PATH="/opt/venv/bin:$PATH"

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]