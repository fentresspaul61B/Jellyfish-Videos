# docker compose up --build

FROM python:3

RUN apt update
RUN apt install python3 -y

WORKDIR /app

COPY . /app/

# Set the path to the credentials file
ENV GOOGLE_APPLICATION_CREDENTIALS /app/credentials/key.json

RUN pip install --no-cache-dir -r requirements.txt


