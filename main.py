from fastapi import FastAPI, UploadFile
from upload_video import upload_video
import os
import shutil
import tempfile

app = FastAPI()


# Start API: uvicorn main:app --reload
# Following Link: http://127.0.0.1:8000/docs 

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name  # Capture the temp file path before the file is 

    # Relative path to the file from the working directory
    oauth2_file_path = 'upload_video.py-oauth2.json'

    # Check if the file exists in the working directory
    if os.path.isfile(oauth2_file_path):
        print(f"{oauth2_file_path} exists.")
    else:
        print(f"{oauth2_file_path} does not exist.")
    # Now that the file is saved, you can pass the path to upload_video
    response = upload_video(
        file_path=temp_file_path, 
        title="Uploaded from FastAPI",
        description="A video uploaded from FastAPI",
        category="22",
        keywords="test, FastAPI",
        privacyStatus="private"
    )

    # Clean up the temp file after upload
    os.unlink(temp_file_path)

    # Return some response or the YouTube video link
    return response

