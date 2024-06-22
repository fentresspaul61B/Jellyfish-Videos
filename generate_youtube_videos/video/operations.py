import os
from icecream import ic
import subprocess


def segment_video(
        input_video_path: str,
        output_dir: str,
        segment_duration: int = 60,
        volume: int = 1) -> str:
    """DESCRIPTION:
    Slices longer video into shorter videos. 

    ARGS:
    - input_video_path (str): Path to long video.
    - output_dir (str): Path where to store the sliced videos.
    - segment_duration (int): How long the video slices should be.
    - volume (int): Use the volume parameter to 
    decrease the volume of the original video (1 is max vol 0 is silent).

    RETURNS:
    output_dir
    """
    # Checking if output dir exists, otherwise, make it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Calculate volume filter expression.
    volume_filter = f"volume={volume}"

    # Construct the ffmpeg command for video segmentation.
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-c:v', 'copy',  # Copy the video stream to avoid re-encoding
        '-map', '0',
        '-segment_time', str(segment_duration),
        '-f', 'segment',
        '-reset_timestamps', '1'
    ]

    # If volume is altered, then we must re-encode audio
    if volume != 1:
        command.extend([
            '-c:a', 'aac',  # Re-encode audio using the AAC codec
            '-filter:a', volume_filter
        ])
    else:
        # Copy the audio stream.
        command.append('-c:a')
        command.append('copy')

    # Creating the file names. These file names do not need a special ID
    # because they are randomly selected to create videos.
    command.append(os.path.join(output_dir, 'jelly_fish_%03d.mp4'))

    # Execute the command.
    subprocess.run(command, check=True)

    return output_dir


def merge_audio_video(
        video_path: str,
        audio_path:  str,
        merged_video_path: str) -> str:
    """DESCRIPTION:
    Adds audio to a video. Used to add the voice to the silent or 
    quiet video.

    ARGS:
    - video_path (str): Path to video to merge with audio.
    - audio_path (str): Path to audio to merge with video.
    - merged_video_path (str): Path to save merged video.

    RETURNS:
    merged_video_path (str)
    """
    # Ensure the output directory exists.
    output_dir = os.path.dirname(merged_video_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Build the FFmpeg command
    command = [
        'ffmpeg',
        '-i', video_path,  # path to the video file
        '-i', audio_path,  # path to the audio file
        '-map', '0:v',     # map the video stream from the first input file
        '-map', '1:a',     # map the audio stream from the second input file
        '-c:v', 'copy',    # copy the video codec
        '-c:a', 'aac',     # encode the audio in AAC format
        '-strict', 'experimental',
        merged_video_path        # path for the output file
    ]

    # Run the FFmpeg command
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    ic(result)

    # Check if FFmpeg command was successful.
    if result.returncode != 0:
        raise Exception('FFmpeg failed', result.stderr)

    return merged_video_path


def fade_and_slice_video(
        input_video_path:  str,
        output_video_path: str,
        audio_length:      int,
        fade_duration:     int = 2) -> str:
    """
    Adds a fade to black to the video, and slices the video after fade is 
    complete.

    ARGS:
    - input_video_path (str): Path to video to fade and slice.
    - output_video_path (str): Path to save video.
    - audio_length (int): Total length of video in seconds.
    - fade_duration (int): How long fade should take in seconds.

    RETURNS:
    output_video_path (str)
    """
    # Total video duration is the length of the audio + length of fade.
    duration = audio_length + fade_duration

    # Construct the FFmpeg command for fading and slicing.
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-filter_complex',
        (
            f"[0:v]trim=duration={duration},"
            f"fade=t=out:st={audio_length}:d={fade_duration}:color=black[v]"
            f"crop=405:720[v]"
        ),
        '-map', '[v]',
        '-map', '0:a',
        '-c:a', 'copy',
        '-preset', 'fast',
        output_video_path
    ]

    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-filter_complex',
        (
            f"[0:v]trim=duration={duration},"
            f"fade=t=out:st={audio_length}:d={fade_duration}:color=black,"
            f"crop=405:720[v]"
        ),
        '-map', '[v]',
        '-map', '0:a',
        '-c:a', 'copy',
        '-preset', 'fast',
        output_video_path
    ]

    try:
        subprocess.run(command, check=True)
    except Exception as e:
        ic(f'An error occurred: {e}')
        return None
    return output_video_path


def burn_subtitles_into_video(
        video: str,
        subtitles: str,
        videos_with_subtitles_dir: str) -> str:
    """DESCRIPTION:
    Burns subtitles into a video file.

    ARGS:
    - video (str): The path to the input video file.
    = subtitles (str): The path to the ASS subtitle file.
    - videos_with_subtitles_dir (str): The directory where the output 
    video will be saved.

    RETURNS:
    videos_with_subtitles_dir (str): The path to the output video file 
    with subtitles.
    """
    ic("HERE ATTEMPTING TO BURN SUBTITLES INTO VIDEO")
    # Ensure the output directory exists
    if not os.path.exists(videos_with_subtitles_dir):
        os.makedirs(videos_with_subtitles_dir)

    # Construct the output file path
    output_video_path = os.path.join(
        videos_with_subtitles_dir, os.path.basename(video))

    # Construct the ffmpeg command to burn subtitles into the video
    command = [
        'ffmpeg',
        '-i', video,
        '-vf', f"ass='{subtitles}'",
        '-c:a', 'copy',
        output_video_path
    ]

    # Execute the command
    subprocess.run(command, check=True)

    return output_video_path
