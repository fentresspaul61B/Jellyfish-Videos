

from fastapi import FastAPI, Query
from starlette.responses import RedirectResponse
from generate_youtube_videos.configs import URL_TO_REDIRECT_TO
from generate_youtube_videos.configs import GCP_PROJECT_ID
from generate_youtube_videos.configs import CLICKED_LINK_TOPIC_ID
from google.cloud import pubsub_v1
import json


app = FastAPI()

# http://127.0.0.1:8000/redirect?source=my_source


# How to run the code locally:
# CD into root dir.
# Run: uvicorn redirect_app.main:app --reload
# To access the redirect app use this URL:
# http://127.0.0.1:8000/redirect?source=INFERENCE_ID

PUBLISHER = pubsub_v1.PublisherClient()


@app.get("/redirect")
def redirect_url(source: str = Query(default="unknown")):
    """DESCRIPTION:

    ARGS:

    RETURNS:
    """

    topic_path = PUBLISHER.topic_path(GCP_PROJECT_ID, CLICKED_LINK_TOPIC_ID)

    data = json.dumps({"INFERENCE_ID": source}).encode("utf-8")

    future = PUBLISHER.publish(topic_path, data)
    print(f"Published message ID: {future.result()}")
    print(source)

    # TODO: Fire pub sub event, to store data in BQ.
    # projects/video-generation-404817/topics/CLICKED-LINK
    return RedirectResponse(url=URL_TO_REDIRECT_TO)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
