# # docker compose up --build

# FROM python:3

# RUN apt update
# RUN apt install python3 -y

# WORKDIR /app

# COPY . /app/

# # Set the path to the credentials file
# ENV GOOGLE_APPLICATION_CREDENTIALS /app/credentials/key.json

# RUN pip install --no-cache-dir -r requirements.txt

# # docker compose up --build
# FROM python:3
# RUN apt update
# RUN apt install python3 -y
# WORKDIR /app
# COPY . /app/
# # Set the path to the credentials file
# ENV GOOGLE_APPLICATION_CREDENTIALS /app/credentials/key.json
# RUN pip install --no-cache-dir -r requirements.txt
# Use an official Python runtime as a parent image
FROM python:3.8-slim
# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
COPY credentials/GOOGLE_APPLICATION_CREDENTIALS.json /app/GOOGLE_APPLICATION_CREDENTIALS.json
# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/GOOGLE_APPLICATION_CREDENTIALS.json"
# Make port 8000 available to the world outside this container
EXPOSE 8000
# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
