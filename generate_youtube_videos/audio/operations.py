import subprocess
from faster_whisper import WhisperModel
from icecream import ic
from helpers.decorators import log_function_call

SUBTITLES_TEMPLATE = "generate_youtube_videos/audio/subtitle_template.txt"


def ffmpeg_duration_command(audio_path: str) -> list:
    """Formats a ffmpeg cli command."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    return command


def run_ffmpeg_command(command: list):
    """Runs a ffmpeg command. Saves to audio path."""
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result


# TODO: Refactor this into smaller functions.
@log_function_call
def get_audio_duration(audio_path: str) -> float:
    """DESCRIPTION:
    Using ffmpeg to get audio duration in seconds.

    ARGS:
    - audio_path (str): Path to audio.

    RETURNS:
    duration (float): Audio duration in seconds.
    """
    result = run_ffmpeg_command(ffmpeg_duration_command(audio_path))
    if result.returncode != 0:
        raise Exception('ffprobe failed', result.stderr)
    duration = float(result.stdout)
    return duration


def extract_segments_and_info(audio: str) -> tuple:
    """"""
    return WhisperModel("small").transcribe(audio)


@log_function_call
def transcribe(audio: str) -> tuple:
    """DESCRIPTION:
    Converts audio into text segments.

    ARGS:
    - audio (str): Path to audio file to transcribe.

    RETURNS:
    language (str), segments (list)
    """
    segments, info = extract_segments_and_info(audio)
    language = info[0]
    return language, list(segments)


def format_time_ass(seconds: float) -> str:
    """DESCRIPTION:
    Formats time into subtitle format ASS.

    ARGS:
    - seconds (float): Time in seconds.

    RETURNS:
    formatted_time (str)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)
    return f"{hours:01d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def make_subtitle_filepath(dir: str, inference_id: str, language: str) -> str:
    """Composes the filepath for the subtitle file to be stored."""
    return f"{dir}/{inference_id}.{language}.ass"


def txt_to_str(filepath: str) -> str:
    """Converts .txt file to a python string"""
    with open(filepath, 'r') as file:
        return file.read()


def format_subtitle_line(start: float, end: float, segment) -> str:
    """Formats a single line to add to the subtitle file. """
    return f"Dialogue: 0,{start},{end},Default,,0,0,0,,{segment.text}\n"


def format_segments(text: str, segments: list) -> str:
    """Iterates over segments, formating into correct ASS subtitle format."""
    for segment in segments:
        start = format_time_ass(segment.start)
        end = format_time_ass(segment.end)
        text += format_subtitle_line(start, end, segment)
    return text


@log_function_call
def generate_subtitle_file_ass(
        language: str,
        segments: list,
        inference_id: str,
        subtitles_dir: str) -> str:
    """DESCRIPTION:
    Creates and saves the subtitle file in ASS format.

    ARGS:
    - language (str): 
    - segments (list): List of time segments.
    - inference_id (str): ID for video.
    - subtitles_dir (str): Path to save subtitles file.

    RETURNS
    filepath (str): subtitle file path
    """
    filepath = make_subtitle_filepath(subtitles_dir, inference_id, language)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(format_segments(txt_to_str(SUBTITLES_TEMPLATE), segments))
    return filepath
