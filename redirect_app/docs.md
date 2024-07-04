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

https://get.docker.com/?_gl=1*ir9fbn*_ga*OTU3NTU5ODI1LjE3MTg4MzQwMDk.*_ga_XJWPQMJYHQ*MTcxOTI5MjAxMS4zLjEuMTcxOTI5MjAzOC4zMy4wLjA.

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

docker pull us-central1-docker.pkg.dev/video-generation-404817/redirect-app/redirect_app_web


gcloud auth print-access-token

docker login -u oauth2accesstoken https://us-central1-docker.pkg.dev
Paste in password

sudo docker pull us-central1-docker.pkg.dev/video-generation-404817/clicked-links/redirect_app_web

gcloud compute firewall-rules create allow-http-8000 \
>     --allow tcp:8000 \
>     --source-ranges 0.0.0.0/0 \
>     --target-tags http-server


http://34.133.138.45:8000/redirect?source=INFERENCE_ID



# IAC
Use terraform to create GCE instance
Use Ansible to install docker, create image, pull code etc ... 

# STUCK:
Was able to get the docker container to start, and to pull the image, but now: 
Unable to make requests to endpoint. 
I have tried this command: 
http://34.133.138.45:8000/redirect?source=INSIDE_GCE

And it just hangs. The IP is from the VM. Also, does not work locally inside the VM when using CURL. 

```
pauls_ml_projects@redirect-app:~$ curl http://0.0.0.0:8000/redirect?source=hello
``` 

runs without errors in VM, but does not create record in BQ. 

```
curl http://34.133.138.45:8000/redirect?source=hello
```

Does not run inside VM, just hangs.
Also found that must use windows VM if want access to virutal display?
But odd that I was given the option to add a virtual display, even though I added the ubuntu os. 


Need to connect host ports of host machine to connect to docker/web. 

How to use Docker reverse proxy?
Reverse proxy set up?

Add another server for load balancing and is response.

Run python server in docker image, then add another server 

Transparent proxy. 

Http -> python_server -> performat_server -> 
Set local IP of docker with 8000

Ngnix

