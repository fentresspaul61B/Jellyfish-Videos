"""

"""
import subprocess
from generate_youtube_videos.video.operations import segment_video
from generate_youtube_videos.video.operations import merge_audio_video
from generate_youtube_videos.video.operations import fade_and_slice_video
from generate_youtube_videos.video.operations import burn_subtitles_into_video

# TODO: Need to add large test video to GCP bucket, and add similar
# logic to pull it down, like the audio tests.

# Not exactly sure yet how to test things like fading/ slicing the
# video, or adding subtitles. Ideas: Slicing can be checked just
# Measuring that the processed video is <= 60 seconds? Fading could be
# tested that the last frame is completely black. And subtitles could
# be verified with some type of image classifier? Seems like doing
# allot just for unit tests.


def test_ffmpeg_available() -> None:
    """DESCRIPTION:

    ARGS:

    RETURNS:
    """
    result = subprocess.run(
        ["ffmpeg", "-version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    message = "FFMPEG not available in current env."
    assert result.returncode == 0, message


def test_segment_video() -> None:
    pass


def test_merge_audio_video() -> None:
    pass


def test_fade_and_slice_video() -> None:
    pass


def test_burn_subtitles_into_video() -> None:
    pass
