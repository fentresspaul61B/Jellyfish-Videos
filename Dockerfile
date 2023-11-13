# Instructions:
# For local testing:
# 1. Build Docker Image: docker build -t my-fastapi-app .
# 2. Run Docker container: docker run -d --name my-fastapi-container -p 8000:8000 my-fastapi-app
# 3. Start the local server: uvicorn main:app --reload
# 4. Visit fast API UI: http://127.0.0.1:8000/docs 
# 5. Or test using: python test_api.py

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# CMD exec gunicorn --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 main:app

CMD exec gunicorn --worker-class uvicorn.workers.UvicornWorker --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 main:app

