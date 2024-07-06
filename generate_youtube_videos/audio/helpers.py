import subprocess
import time
from datetime import datetime
# from functools import wraps
from typing import Callable
from icecream import ic
import inspect
# import logging
from google.cloud import storage
import tempfile
import os
# from file_operations import pull_test_history_data_from_GCP


def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage

    Args:
    bucket_name (str): Name of the GCS bucket.
    source_file_name (str): Path to the file to upload.
    destination_blob_name (str): The desired name for your file in the bucket.

    Returns:
    str: GCS URL of the uploaded file
    """
    # Initialize a storage client using your service account key
    storage_client = storage.Client()

    # Get the bucket object
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob and upload the file's content to GCS
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    # The public URL can be used to access the file directly via HTTP
    return f"gs://{bucket_name}/{destination_blob_name}"


# Example usage
if __name__ == "__main__":
    bucket_name = 'videos-with-subtitles'
    source_file_name = '/Users/paulfentress/Desktop/Jellyfish/VIDEOS_WITH_SUBTITLES'
    destination_blob_name = 'destination-filename-in-gcs'

    uploaded_file_url = upload_to_gcs(
        bucket_name, source_file_name, destination_blob_name)
    print(f"File uploaded to {uploaded_file_url}")


def log_data(func: Callable) -> Callable:

    def wrapper(*args, **kwargs):
        # Get function name
        func_name = func.__name__

        # Get input arguments and their types
        input_args = args
        input_kwargs = kwargs
        input_types = [type(arg).__name__ for arg in args] + \
            [f"{key}: {type(value).__name__}" for key, value in kwargs.items()]

        # Timestamp of when the function was called
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Start time
        start_time = time.time()

        # Execute the function and get the result
        result = func(*args, **kwargs)

        # End time
        end_time = time.time()
        duration = end_time - start_time

        # Get output type
        output_type = type(result).__name__

        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        file_path = outer_frames[1].filename

        # ic the collected information
        ic()
        print(f"Function Name: {func_name}")
        print(f"Source File: {file_path}")
        print(f"Call Time: {timestamp}")
        print(timestamp)
        print("Input Arguments:")
        print(input_args)
        print("Input Keyword Arugments:")
        print(input_kwargs)
        print("Input Data Types:")
        print(input_types)
        print("Output Data Types:")
        print(output_type)
        print(f"Execution Time: {duration}")
        print()

        return result

    return wrapper


def run_ffmpeg_command(command: list):
    """Runs a ffmpeg command. Saves to audio path."""
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result
