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
        temp_file_path = temp_file.name  # Capture the temp file path before the file is closed

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

