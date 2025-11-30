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
