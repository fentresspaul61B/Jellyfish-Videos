# OS used for directory actions.
import os
import shutil
from google.cloud import storage
from icecream import ic
import tempfile
import pandas as pd

from configs import DESKTOP_PATH
from configs import GOOGLE_SHEET_NAME
from configs import RAW_AUDIO
from configs import ONE_MINUTE_VIDEOS
from configs import VIDEOS_MERGED_WITH_AUDIO
from configs import FADED_AND_SLICED_VIDEOS
from configs import VIDEOS_WITH_SUBTITLES
from configs import HISTORY
from configs import SUBTITLES
from configs import ROOT_DIR
from configs import TEST_DATA_BUCKET_GCP


def initialize_empty_directories(output_dir: str = None):
    """
    DESCRIPTION:
    Multiple directories are created for the pipeline, because the files
    change from audio, to video, and cannot have these transformations
    applied in place.

    ARGS:
    - output_dir (str): Path where the generated data will be stored.

    RETURNS:
    output_dir (str)
    """

    if not output_dir:
        # If no path passed, then use desktop.
        output_dir = os.path.join(DESKTOP_PATH, GOOGLE_SHEET_NAME)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Creating sub dirs.
    os.mkdir(os.path.join(output_dir, RAW_AUDIO))
    os.mkdir(os.path.join(output_dir, ONE_MINUTE_VIDEOS))
    os.mkdir(os.path.join(output_dir, VIDEOS_MERGED_WITH_AUDIO))
    os.mkdir(os.path.join(output_dir, FADED_AND_SLICED_VIDEOS))
    os.mkdir(os.path.join(output_dir, VIDEOS_WITH_SUBTITLES))
    os.mkdir(os.path.join(output_dir, HISTORY))
    os.mkdir(os.path.join(output_dir, SUBTITLES))

    return output_dir


FINAL_DATA = [HISTORY, VIDEOS_WITH_SUBTITLES]
INTERMEDIARY_DATA = [
    ONE_MINUTE_VIDEOS,
    VIDEOS_MERGED_WITH_AUDIO,
    FADED_AND_SLICED_VIDEOS,
    RAW_AUDIO,
    SUBTITLES
]


def delete_dir(full_path: str) -> None:
    """DESCRIPTION:
    Deletes dir at full path.

    ARGS:
    - path (str): Path to dir to be deleted.

    RETURNS: None
    """
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        print(f"Directory '{full_path}' has been deleted.")
    else:
        print(f"The directory '{full_path}' does not exist.")


def delete_dirs(dirs: list) -> None:
    """DESCRIPTION:
    Removes video and audio data, that is created in the process of
    making the final videos.

    ARGS:
    - dirs (list): List of strings to paths to remove.

    RETURNS: None
    """

    for dir in dirs:
        full_path = os.path.join(ROOT_DIR, dir)
        try:
            delete_dir(full_path)
        except Exception as e:
            print(f"Error occurred while deleting directory: {e}")
    pass


def clean_up_post_run():
    """DESCRIPTION:
    Removes video and audio data, that is created in the process of
    making the final videos. Does not delete final data which needs to 
    be saved for upload step.

    ARGS: None

    RETURNS: None
    """
    delete_dirs(INTERMEDIARY_DATA)


def clean_up_pre_run():
    """DESCRIPTION:
    Removes video and audio data, that is created in the process of
    making the final videos as well as the final data. Used for pre 
    runs.

    ARGS: None

    RETURNS: None
    """
    delete_dirs(INTERMEDIARY_DATA)
    delete_dirs(FINAL_DATA)
    delete_dir(ROOT_DIR)


def pull_test_history_data_from_GCP() -> pd.DataFrame:
    """DESCRIPTION:
    Pulls down the history dataframe GCP. Save it as a file in a temp
    folder. Converts CSV to dataframe, and returns the dataframe.

    ARGS: None

    RETURNS:
    df (pd.DataFrame)
    """
    client = storage.Client()
    bucket_name = f"{TEST_DATA_BUCKET_GCP}"
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="Jellyfish/HISTORY/")

    df = pd.DataFrame()

    with tempfile.TemporaryDirectory() as temp_output_dir:
        for blob in blobs:
            name = os.path.basename(blob.name)
            if name == "Jellyfish.csv":
                file_name = os.path.join(temp_output_dir, name)
                blob.download_to_filename(file_name)
                df = pd.read_csv(file_name, index_col=0)

    return df


def download_audio_files_from_gcp(bucket_name, prefix, temp_dir):
    """Download audio files from a specified GCP bucket into a temporary directory."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    audio_files = []

    for blob in blobs:
        name = os.path.basename(blob.name)
        if name.endswith(".mp3"):
            local_path = os.path.join(temp_dir, name)
            blob.download_to_filename(local_path)
            audio_files.append(local_path)

    return audio_files


def main():
    ic(pull_test_history_data_from_GCP().shape)


if __name__ == "__main__":
    main()
