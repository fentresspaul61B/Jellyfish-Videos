"""
A common pattern for these tests, is to pull data down from GCP, store 
it in a temp directory, do the test on the data in the temp directory
and then continue. The reason being is I do not want large files 
stored locally, which often cause downstream issues when pushing to 
GitHub.
"""

import pandas as pd
import tempfile
import os
from icecream import ic
from google.cloud import storage
import httpx
from generate_youtube_videos.audio.generation import generate_raw_audio_files
from generate_youtube_videos.audio.operations import get_audio_duration
from generate_youtube_videos.audio.operations import transcribe
from generate_youtube_videos.audio.operations import format_time_ass
from generate_youtube_videos.audio.operations import generate_subtitle_file_ass
from generate_youtube_videos.file_operations import pull_test_history_data_from_GCP
from generate_youtube_videos.file_operations import download_audio_files_from_gcp
from generate_youtube_videos.audio.generation import get_scripts
from generate_youtube_videos.audio.generation import create_api_jobs
from generate_youtube_videos.audio.generation import call_api
from generate_youtube_videos.audio.generation import generate_raw_audio_files
from generate_youtube_videos.audio.generation import SpeechJob
from generate_youtube_videos.audio.generation import SpeechApiData
import shutil
from configs import TEST_DATA_BUCKET_GCP

TESTING_DF = pull_test_history_data_from_GCP()


def setup_test_environment() -> tuple:
    temp_output_dir = tempfile.TemporaryDirectory()
    temp_csv_path = os.path.join(temp_output_dir.name, 'Jellyfish.csv')
    TESTING_DF.to_csv(temp_csv_path, index=False)
    job = SpeechJob(temp_csv_path, temp_output_dir.name)
    return temp_output_dir, temp_csv_path, job


def setup_tests(function):
    temp_output_dir, _, job = setup_test_environment()
    passed = False
    try:
        scripts = function(job)
        assert isinstance(scripts, tuple)
        assert len(scripts) == 2
        passed = True
    finally:
        shutil.rmtree(temp_output_dir.name)
    return passed


def test_get_scripts():
    assert setup_tests(get_scripts)


def test_create_api_jobs():
    assert setup_tests(create_api_jobs)


def test_call_api():
    temp_output_dir, _, job = setup_test_environment()
    try:
        jobs = create_api_jobs(job)
        response = call_api(jobs[0])
        ic(response)
        assert response
    finally:
        shutil.rmtree(temp_output_dir.name)


# def test_generate_speech():
#     temp_output_dir, _, job = setup_test_environment()
#     try:
#         jobs = create_api_jobs(job)
#         response = generate_speech(jobs[0])
#         ic(os.listdir(temp_output_dir.name))
#         assert response
#     finally:
#         shutil.rmtree(temp_output_dir.name)


def test_generate_raw_audio_files():
    temp_output_dir, temp_csv_path, job = setup_test_environment()
    try:
        result = generate_raw_audio_files(temp_csv_path, temp_output_dir.name)
        files = [file for file in os.listdir(result) if file.endswith(".mp3")]
        assert files
        assert len(files) == 2
    finally:
        shutil.rmtree(temp_output_dir.name)


def test_get_audio_duration():
    """DESCRIPTION:
    Pulls 2 audio samples from GCP. Checks the length of the audio 
    files. Makes sure the length is long enough.

    ARGS: None

    RETURNS: None
    """
    with tempfile.TemporaryDirectory() as temp_output_dir:
        audio_files = download_audio_files_from_gcp(
            bucket_name=TEST_DATA_BUCKET_GCP,
            prefix="Jellyfish/RAW_AUDIO/",
            temp_dir=temp_output_dir
        )

        for file_name in audio_files:
            audio_duration = get_audio_duration(file_name)
            duration = 30
            # Testing if audio duration function works, and that
            # it returns seconds > 30.
            message = f"Audio duration not longer than {duration} seconds."
            assert audio_duration > duration, message
            pass


def calculate_percent_difference(length_actual: int, length_result: int) -> float:
    numerator = abs(length_actual - length_result)
    denom = ((length_actual + length_result) / 2)
    return numerator / denom * 100


def test_transcribe():
    """DESCRIPTION:
    Test transcription accuracy.

    ARGS: None

    RETURNS: None
    """
    with tempfile.TemporaryDirectory() as temp_output_dir:
        audio_files = download_audio_files_from_gcp(
            bucket_name=TEST_DATA_BUCKET_GCP,
            prefix="Jellyfish/RAW_AUDIO/",
            temp_dir=temp_output_dir
        )
        # Assume TESTING_DF is defined elsewhere
        video_transcript = TESTING_DF.to_dict()["VIDEO_SCRIPT"][0]

        for file_name in audio_files:
            language, segments = transcribe(audio=file_name)
            transcription = ''.join(segment.text for segment in segments)

            num_characters_actual = len(video_transcript)
            num_characters_predicted = len(transcription)

            percent_difference = calculate_percent_difference(
                num_characters_actual, num_characters_predicted)

            threshold = 10
            message = f"% dif in num chars > {threshold}%."
            assert percent_difference < threshold, message

            message = "Language transcribed is not english."
            assert language == "en", message
            pass


def test_format_time_ass():
    """DESCRIPTION:
    Tests multiple cases for formatting the time strings used to 
    generate subtitles in ASS format. Time is in the form of hours, 
    minutes, seconds, and centiseconds

    3661.25 seconds -> "1:01:01.00"
    Explanation:
    1 hour = 3600 seconds
    1 minute = 60 seconds

    So we have 3600 + 60 + 1.00 which makes 1:01:01.00 in english is
    1 hour, 1 minute, and 1 second, with 0 centi seconds.

    Note:
    The function rounds centi seconds, so they are not included in the
    tests.

    ARGS: None

    RETURNS: None
    """
    # Simple case.
    message = "Failed simple case."
    assert format_time_ass(3661.00) == "1:01:01.00", message

    # Test the formatting of zero seconds
    message = "Failed formatting of zero seconds."
    assert format_time_ass(0) == "0:00:00.00", message

    # Test the formatting where rounding is significant.
    message = "Failed tricky rounding case."
    assert format_time_ass(3599.00) == "0:59:59.00", message

    # Testing large number.
    message = "Failed testing large number."
    assert format_time_ass(86399.00) == "23:59:59.00", message

    pass


def test_generate_subtitle_file_ass():
    """DESCRIPTION:

    ARGS: None

    RETURNS: None
    """

    with tempfile.TemporaryDirectory() as temp_output_dir:

        audio_files = download_audio_files_from_gcp(
            bucket_name=TEST_DATA_BUCKET_GCP,
            prefix="Jellyfish/RAW_AUDIO/",
            temp_dir=temp_output_dir
        )

        for file_name in audio_files:
            basename = os.path.basename(file_name)
            inference_id = basename.strip(".mp3")
            language, segments = transcribe(file_name)
            file_path = generate_subtitle_file_ass(
                language=language,
                segments=segments,
                inference_id=inference_id,
                subtitles_dir=temp_output_dir
            )

            required_sections = {
                '[Script Info]',
                '[V4+ Styles]',
                '[Events]'
            }
            found_sections = set()

            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line in required_sections:
                        found_sections.add(line)

            # Check if all required sections are found
            message = "Did not find required .ASS sections."
            assert found_sections == required_sections, message


def main():
    pass


if __name__ == "__main__":
    main()