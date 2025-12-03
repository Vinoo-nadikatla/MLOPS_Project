FROM python:3.10-slim

# Do not write pyc files and run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps required for some Python packages and for building wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Create non-root user and give ownership
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Default environment variables (can be overridden at runtime)
ENV MODEL_PATH=src/models/model.pkl \
    CONFIG_PATH=data/processed/preprocess_config.json \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

# Healthcheck using Python stdlib (no extra deps)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD python -c "import urllib.request,sys
try:
    r=urllib.request.urlopen('http://127.0.0.1:8000/health')
    sys.exit(0)
except Exception:
    sys.exit(1)"

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/app /app
ENV MODEL_PATH=/app/models/model.pkl
# If you want to copy a sample model for demo inside image (optional)
# COPY models/model.pkl /app/models/model.pkl
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
