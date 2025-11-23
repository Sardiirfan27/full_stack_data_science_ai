FROM apache/airflow:2.7.1-python3.11

# Copy the current directory contents to /app in the container
COPY docker/streamlit/requirements.txt .

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Install Python packages for the airflow user
USER airflow
RUN pip install --user --no-cache-dir -r requirements.txt

# ENV PATH="/home/airflow/.local/bin:${PATH}"

WORKDIR /opt/project

