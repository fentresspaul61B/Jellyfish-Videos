
# Use the official lightweight Python image.
# https://hub.docker.com/_/python

# 1. docker image build -t python:0.0.1 .
# 2. Listing the images: docker images
# 3. docker run [IMAGE_ID]
# 4. docker contain rm [CONTAINER_ID]
# 5. REMOVE: docker image rm [IMAGE_ID]


# docker image rm d1430e988087 -f (force remvoes an image)
# docker run -d --name jelly_fish_app -v /Users/paulfentress/Desktop/:/app/Jellyfish [IMAGE_ID]


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
CMD ["python3", "generate_youtube_videos.py"]

