# Use official Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy application code to the container
COPY web_app/ .

# Copy the current directory contents to /app in the container
COPY docker/streamlit/requirements.txt .

# Install dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#  && pip install --no-cache-dir -r requirements.txt \
#  && apt-get purge -y --auto-remove build-essential \
#  && rm -rf /var/lib/apt/lists/*

 RUN pip install --no-cache-dir -r requirements.txt



# Set environment variable to prevent Streamlit from opening browser
ENV STREAMLIT_SERVER_HEADLESS=true

#PYTHONUNBUFFERED=1 : Ensures Python logs and prints are immediately flushed to stdout
# You can see logs in real-time when you do docker logs <container>
ENV PYTHONUNBUFFERED=1 

# Optional: read environment variables from .env file
# ENV DOTENV_PATH=.env


# Expose Streamlit default port
EXPOSE 8501

# Command to run Streamlit
# "--server.enableCORS=false" : Disable CORS
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 
