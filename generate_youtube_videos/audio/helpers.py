from types import MappingProxyType
import subprocess
import time
from datetime import datetime
from typing import Callable
from icecream import ic
import inspect
from google.cloud import storage
from functools import wraps
from colorama import init, Fore, Style
# from file_operations import pull_test_history_data_from_GCP
# import tempfile
# import os
# import logging
# from functools import wraps

# Define ANSI escape codes for colors


COLOR_CODES = MappingProxyType(
    {
        "RED": "\033[91m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "BLUE": "\033[94m",
        "MAGENTA": "\033[95m",
        "CYAN": "\033[96m",
        "WHITE": "\033[97m",
        "RESET": "\033[0m"
    }
)


# Initialize colorama
init(autoreset=True)


# TODO: Refactor this function (break into smaller functions).
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


def get_function_name(func: Callable) -> str:
    return func.__name__


def create_time_stamp() -> datetime:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_time_now() -> time:
    return time.time()


def print_in_color(message: str, color: str) -> None:
    """Prints message in color."""
    print(color + message)


def print_formatted_func_name(
        func_name: str, color: str = COLOR_CODES["CYAN"]) -> None:
    print_in_color(f"Function Name: {func_name}", color)


# TODO: Refactor this function (break into smaller functions).
def wrapper_helper(func, *args, **kwargs):
    func_name = get_function_name(func)
    timestamp = create_time_stamp()
    start_time = get_time_now()
    print_formatted_func_name(func_name=func_name)
    frame = inspect.currentframe()
    outer_frames = inspect.getouterframes(frame)
    file_path = outer_frames[1].filename
    print(f"Source File: {file_path}")
    print(f"Call Time: {timestamp}")

    # Get input arguments and their types
    input_args = args
    input_kwargs = kwargs
    input_types = [type(arg).__name__ for arg in args] + \
        [f"{key}: {type(value).__name__}" for key, value in kwargs.items()]

    print("Input Arguments:")
    ic(input_args)

    print("Input Keyword Arugments:")
    ic(input_kwargs)

    print("Input Data Types:")
    ic(input_types)

    # Execute the function and get the result
    result = func(*args, **kwargs)
    print("Output Data:")
    ic(result)

    # End time
    end_time = time.time()
    duration = end_time - start_time

    # Get output type
    output_type = type(result).__name__

    # ic the collected information
    print("Output Data Types:")
    ic(output_type)
    print(f"Execution Time: {duration}")
    print()

    return result


# def log_data(func: Callable) -> Callable:
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         return wrapper_helper(func, *args, **kwargs)
#     return wrapper


def first_order_function(func: Callable) -> Callable:
    """Decorator used print useful messages for first order functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print()
        print(Fore.YELLOW + f"FIRST ORDER FUNCTION")
        return wrapper_helper(func, *args, **kwargs)
    return wrapper


def higher_order_function(func: Callable) -> Callable:
    """Decorator used print useful messages for higher order functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print()
        print(Fore.YELLOW + Style.BRIGHT + f"HIGHER ORDER FUNCTION")
        return wrapper_helper(func, *args, **kwargs)
    return wrapper


@first_order_function
def run_ffmpeg_command(command: list):
    """Runs a ffmpeg command. Saves to audio path."""
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result


def main():
    bucket_name = 'videos-with-subtitles'
    source_file_name = '/Users/paulfentress/Desktop/Jellyfish/VIDEOS_WITH_SUBTITLES'
    destination_blob_name = 'destination-filename-in-gcs'

    uploaded_file_url = upload_to_gcs(
        bucket_name,
        source_file_name,
        destination_blob_name
    )
    print(f"File uploaded to {uploaded_file_url}")


# Example usage
if __name__ == "__main__":
    main()
