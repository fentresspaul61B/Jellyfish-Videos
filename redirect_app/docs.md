# Redirect API

Uses API to track when a video was clicked, and which video was clicked,
saves data to a database. Used to measure the effectiveness of the generated 
content.

Solved this by using a pub sub bigquery connection, which stores the inference
ID in BQ with other meta data.

Need to save data to bigquery, so that the inference ID that is saved
from the URL, and be used to trace back to the original video, and 
youtube link.

## How to run script from within docker container: 
cd into the redirect_app dir. 
```docker compose up --build```
Go to this URL and change the "source" value
http://127.0.0.1:8000/redirect?source=INFERENCE_ID

## Pushing docker image to GCP
List all images:
docker images
docker tag redirect_app_web gcr.io/video-generation-404817/redirect_app_web 
docker push gcr.io/video-generation-404817/redirect_app_web

Created a docker repo on GCP.
Need to authenticate GCP docker helper. 
gcloud auth configure-docker \
    us-central1-docker.pkg.dev

LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE

To find valid locations
gcloud artifacts locations list

LOCATION: us-central1
PROJECT_ID: video-generation-404817
REPOSITORY: clicked-links
IMAGE: redirect_app_web

us-central1-docker.pkg.dev/video-generation-404817/clicked-links/redirect_app_web

tag the docker image:
docker tag SOURCE-IMAGE LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG

If tag is not specified, GCP will add "latest" which should be fine. 
docker tag redirect_app_web us-central1-docker.pkg.dev/video-generation-404817/clicked-links/redirect_app_web

Check if tagged: 

gcloud artifacts repositories describe REPOSITORY \
    --project=PROJECT-ID \
    --location=LOCATION

gcloud artifacts repositories describe clicked-links --project=video-generation-404817 --location=us-central1

PUSH TO THE REPO:

docker push LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE

docker push us-central1-docker.pkg.dev/video-generation-404817/clicked-links/redirect_app_web


http://34.133.138.45:8000/redirect?source=INFERENCE_ID


# IAC
Use terraform to create GCE instance
Use Ansible to install docker, create image, pull code etc ... 

# STUCK:
Stuck on pulling docker image from GCP repo into GCE server. Able to
download docker, and pull public hello world image, but unable to 
pull my own down. 

This command is failing: 
```bash
pauls_ml_projects@redirect-app:~$ sudo docker pull us-central1-docker.pkg.dev/video-generation-404817/clicked-links/redirect_app_web
Using default tag: latest
Error response from daemon: Head "https://us-central1-docker.pkg.dev/v2/video-generation-404817/clicked-links/redirect_app_web/manifests/latest": denied: Unauthenticated request. Unauthenticated requests do not have permission "artifactregistry.repositories.downloadArtifacts" on resource "projects/video-generation-404817/locations/us-central1/repositories/clicked-links" (or it may not exist)
```

Also found that must use windows VM if want access to virutal display?
But odd that I was given the option to add a virtual display, even though I added the ubuntu os. 

