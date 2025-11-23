FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# COPY fastapi_app/ .   
COPY fastapi_app/ .

COPY ./docker/fastapi/requirements.txt .

RUN pip install --no-cache-dir --timeout 50 -r requirements.txt


ENV MLFLOW_TRACKING_URI=http://mlflow:5000

EXPOSE 8000
# Jalankan FastAPI dengan Gunicorn + Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
