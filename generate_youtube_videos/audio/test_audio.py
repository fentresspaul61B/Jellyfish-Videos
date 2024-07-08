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
from generate_youtube_videos.audio.generation import _get_script_and_id_tuples_from_csv
from generate_youtube_videos.audio.generation import _create_open_ai_api_tts_jobs
from generate_youtube_videos.audio.generation import _call_open_ai_tts_api
from generate_youtube_videos.audio.generation import generate_raw_audio_files
from generate_youtube_videos.audio.generation import _pick_random_voice
from generate_youtube_videos.audio.generation import SpeechJob
from generate_youtube_videos.audio.generation import SpeechApiData
import shutil
from configs import TEST_DATA_BUCKET_GCP

TESTING_DF = pull_test_history_data_from_GCP()


def setup_test_environment() -> tuple:
    """Sets up the testing env, with a temp output dir, the csv data which 
    include the video scripts, as well as the speech generation job. This is 
    used within a decorator function, to make for easier testing.
    Has I/O operations."""
    temp_output_dir = tempfile.TemporaryDirectory()
    temp_csv_path = os.path.join(temp_output_dir.name, 'Jellyfish.csv')
    TESTING_DF.to_csv(temp_csv_path, index=False)
    # job = SpeechJob(temp_csv_path, temp_output_dir.name)
    return temp_output_dir, temp_csv_path


def setup_kwargs(kwargs, temp_output_dir, temp_csv_path):
    """Formating kwargs for decorator. Has no I/O operations."""
    kwargs['temp_output_dir'] = temp_output_dir
    kwargs['temp_csv_path'] = temp_csv_path
    return kwargs


def setup_test(func):
    """Add this decorator to set up testing env, with a temp output dir, 
    the testing CSV file from GCP, Speech job to run the tests.
    Has I/O operations."""
    def wrapper(*args, **kwargs):
        temp_output_dir, temp_csv_path = setup_test_environment()
        kwargs = setup_kwargs(kwargs, temp_output_dir, temp_csv_path)
        result = func(*args, **kwargs)
        temp_output_dir.cleanup()
        return result
    return wrapper


def percent_difference(length_actual: int, length_result: int) -> float:
    """Has no I/O operations."""
    numerator = abs(length_actual - length_result)
    denom = ((length_actual + length_result) / 2)
    return numerator / denom * 100


def test__pick_random_voice():
    from generate_youtube_videos.configs import GPT_VOICES
    voice = _pick_random_voice()
    assert voice
    assert isinstance(voice, str)
    assert isinstance(GPT_VOICES, tuple)


@setup_test
def test_get_scripts(temp_output_dir, temp_csv_path):
    "Has I/O operations."
    scripts = _get_script_and_id_tuples_from_csv(
        SpeechJob(temp_csv_path, temp_output_dir.name))
    assert isinstance(scripts, tuple)
    assert len(scripts) == 2


@setup_test
def test_create_api_jobs(temp_output_dir, temp_csv_path):
    "Has I/O operations."
    scripts = _create_open_ai_api_tts_jobs(
        SpeechJob(temp_csv_path, temp_output_dir.name))
    assert isinstance(scripts, tuple)
    assert len(scripts) == 2
    ids_match = scripts[0].inference_id == scripts[1].inference_id
    scripts_match = scripts[0].input == scripts[1].input
    assert not ids_match, "Api jobs have duplicate IDs."
    assert not scripts_match, "Api jobs have duplicate scripts."


@setup_test
def test_call_api(temp_output_dir, temp_csv_path):
    "Has I/O operations."
    jobs = _create_open_ai_api_tts_jobs(
        SpeechJob(temp_csv_path, temp_output_dir.name))
    response = _call_open_ai_tts_api(jobs[0])
    assert response


@setup_test
def test_decorator(temp_output_dir, temp_csv_path):
    "Has I/O operations."
    # Validate that the temp directory and CSV file are set up correctly
    assert os.path.exists(temp_output_dir.name)
    assert os.path.isfile(temp_csv_path)


@setup_test
def test_generate_raw_audio_files(temp_output_dir, temp_csv_path):
    "Has I/O operations."
    job = SpeechJob(temp_csv_path, temp_output_dir.name)
    result = generate_raw_audio_files(job)
    files = [file for file in os.listdir(result) if file.endswith(".mp3")]
    assert files
    assert len(files) == 2


# TODO: Refactor and add new decorator if need to pull audio files.
def test_get_audio_duration():
    """DESCRIPTION:
    Pulls 2 audio samples from GCP. Checks the length of the audio 
    files. Makes sure the length is long enough. Has I/O operations.

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


def test_transcribe():
    """DESCRIPTION:
    Test transcription accuracy. Has I/O operations.

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

            precent_diff = percent_difference(
                num_characters_actual, num_characters_predicted)

            threshold = 10
            message = f"% dif in num chars > {threshold}%."
            assert precent_diff < threshold, message

            message = "Language transcribed is not english."
            assert language == "en", message
            pass


def test_format_time_ass():
    """DESCRIPTION:
    Tests multiple cases for formatting the time strings used to 
    generate subtitles in ASS format. Time is in the form of hours, 
    minutes, seconds, and centiseconds. 

    3661.25 seconds -> "1:01:01.00"
    Explanation:
    1 hour = 3600 seconds
    1 minute = 60 seconds

    So we have 3600 + 60 + 1.00 which makes 1:01:01.00 in english is
    1 hour, 1 minute, and 1 second, with 0 centi seconds.
    Has I/O operations.

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
    """DESCRIPTION: Has I/O operations.

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
