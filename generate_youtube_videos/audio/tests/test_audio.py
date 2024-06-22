import pandas as pd
import tempfile
import os
from icecream import ic

from generate_youtube_videos.audio.generation import generate_raw_audio_files
from generate_youtube_videos.audio.operations import get_audio_duration
from generate_youtube_videos.audio.operations import transcribe
from generate_youtube_videos.audio.operations import format_time_ass
from generate_youtube_videos.audio.operations import generate_subtitle_file_ass


HISTORY_CSV = "generate_youtube_videos/audio/tests/files_for_testing/Jellyfish.csv"
TESTING_DF = pd.read_csv(HISTORY_CSV, index_col=0)
TEST_AUDIO_1 = "generate_youtube_videos/audio/tests/files_for_testing/5f4e7edb-a590-4217-9572-f4b55f170e76.mp3"
TEST_AUDIO_2 = "generate_youtube_videos/audio/tests/files_for_testing/9a3efaa5-ecea-4faf-bb15-b621a0c4b96c.mp3"


def test_generate_raw_audio_files():
    with tempfile.TemporaryDirectory() as temp_output_dir:
        result_dir = generate_raw_audio_files(HISTORY_CSV, temp_output_dir)
        files = os.listdir(result_dir)
        assert len(files) > 0, "No files generated in the output directory."


def test_get_audio_duration():
    audio_1_duration = get_audio_duration(TEST_AUDIO_1)
    audio_2_duration = get_audio_duration(TEST_AUDIO_2)
    durations = [0, 10, 20, 30]
    for duration in durations:
        message = f"Audio duration not longer than {duration} seconds."
        assert audio_1_duration > duration, message
        assert audio_2_duration > duration, message
    pass


def calcluate_percent_difference(length_actual: int, length_result: int) -> float:
    numerator = abs(length_actual - length_result)
    denom = ((length_actual + length_result) / 2)
    return numerator / denom * 100


def test_transcribe():
    """DESCRIPTION:
    Tests if the percent difference in number of characters from the
    transcribed audio, and the text input is less than 10%. Audio needs
    to be transcribed, in order to extract time segments to create
    subtitles.

    ARGS: None

    RETURNS: None
    """
    video_transcript = TESTING_DF.to_dict()["VIDEO_SCRIPT"][0]
    language, segments = transcribe(audio=TEST_AUDIO_2)
    transcription = ""
    for segment in segments:
        transcription += segment.text

    num_characters_actual = len(video_transcript)
    num_characters_predicted = len(transcription)

    percent_difference = calcluate_percent_difference(
        num_characters_actual, num_characters_predicted)

    threshold = 10

    message = f"Percent dif in num characters is greater than {threshold}%."
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
        inference_id = TEST_AUDIO_1.split("/")[-1].strip(".mp3")
        language, segments = transcribe(TEST_AUDIO_1)
        file_path = generate_subtitle_file_ass(
            language=language,
            segments=segments,
            inference_id=inference_id,
            subtitles_dir=temp_output_dir
        )

        required_sections = {'[Script Info]', '[V4+ Styles]', '[Events]'}
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
    # ic(TESTING_DF.to_dict()["VIDEO_SCRIPT"][0])
    ic(test_transcribe())
    pass


if __name__ == "__main__":
    main()
