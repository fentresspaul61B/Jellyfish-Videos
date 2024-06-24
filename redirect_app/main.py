"""
# How to run the code locally:
# CD into root dir.
# Run: uvicorn redirect_app.main:app --reload
# To access the redirect app use this URL:
# http://127.0.0.1:8000/redirect?source=INFERENCE_ID
"""

from fastapi import FastAPI, Query
from starlette.responses import RedirectResponse
from google.cloud import pubsub_v1
import json
from configs import URL_TO_REDIRECT_TO
from configs import GCP_PROJECT_ID
from configs import CLICKED_LINK_TOPIC_ID


app = FastAPI()

PUBLISHER = pubsub_v1.PublisherClient()
TOPIC_PATH = PUBLISHER.topic_path(GCP_PROJECT_ID, CLICKED_LINK_TOPIC_ID)


@app.get("/redirect")
def redirect_url(source: str = Query(default="unknown")):
    """DESCRIPTION:
    Redirects clicks on this URL, to the target URL for donations
    URL_TO_REDIRECT_TO. Data is logged in bigquery using pub-sub. 
    Pub-sub is used for low latency. Only the INFERENCE_ID is 
    collected, and additional meta data is added automatically by pub
    sub.

    ARGS:

    RETURNS:
    """
    data = json.dumps({"INFERENCE_ID": source}).encode("utf-8")
    _ = PUBLISHER.publish(TOPIC_PATH, data=data)
    return RedirectResponse(url=URL_TO_REDIRECT_TO)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
