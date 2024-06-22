import subprocess
from faster_whisper import WhisperModel
from icecream import ic


def get_audio_duration(audio_path: str) -> float:
    """DESCRIPTION:
    Using ffmpeg to get audio duration in seconds.

    ARGS:
    - audio_path (str): Path to audio.

    RETURNS:
    duration (float): Audio duration in seconds.
    """
    # Run the ffprobe command to get the duration of the audio file.
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]

    # Execute the command and capture the output.
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Check if ffprobe command was successful.
    if result.returncode != 0:
        raise Exception('ffprobe failed', result.stderr)

    # Parse the output to get the duration as a float and return it.
    duration = float(result.stdout)

    return duration


def transcribe(audio: str) -> tuple:
    """DESCRIPTION:
    Converts audio into text segments.

    ARGS:
    - audio (str): Path to audio file to transcribe.

    RETURNS:
    language (str), segments (list)
    """
    model = WhisperModel("small")
    segments, info = model.transcribe(audio)
    language = info[0]
    ic("Transcription language", info[0])
    segments = list(segments)
    for segment in segments:
        # ic(segment)
        ic("[%.2fs -> %.2fs] %s" %
           (segment.start, segment.end, segment.text))
    return language, segments


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
    formatted_time = f"{hours:01d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    return formatted_time


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
    subtitle_file (str): subtitle file path
    """
    subtitle_file = f"{subtitles_dir}/{inference_id}.{language}.ass"
    text = ""

    # ASS Header: TODO: Add this to configs file, the format part.
    text += "[Script Info]\n"
    text += "Title: Audio Transcription\n"
    text += "ScriptType: v4.00+\n"
    text += "WrapStyle: 0\n"
    text += "PlayDepth: 0\n"
    text += "Collisions: Normal\n"
    text += "ScaledBorderAndShadow: yes\n"
    text += "Original Script: Your Name\n"
    text += "\n"
    text += "[V4+ Styles]\n"
    text += "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
    text += "Style: Default,Arial,12,&H003a98fc,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1\n"
    text += "\n"
    text += "[Events]\n"
    text += "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    # ASS Events
    for segment in segments:
        segment_start = format_time_ass(segment.start)
        segment_end = format_time_ass(segment.end)
        text += f"Dialogue: 0,{segment_start},{segment_end},Default,,0,0,0,,{segment.text}\n"

    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write(text)

    return subtitle_file
