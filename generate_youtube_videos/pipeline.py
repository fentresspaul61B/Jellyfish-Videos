# Add the Jellyfish-Videos directory to sys.path
import sys
from configs import NUM_VIDEOS_TO_GENERATE
from configs import SUBTITLES
from configs import VIDEOS_WITH_SUBTITLES
from configs import FADED_AND_SLICED_VIDEOS
from configs import VIDEOS_MERGED_WITH_AUDIO
from configs import RAW_AUDIO
from configs import GOOGLE_SHEET_NAME
from configs import HISTORY
from configs import ONE_MINUTE_VIDEOS
from generate_youtube_videos.file_operations import clean_up_pre_run
from generate_youtube_videos.file_operations import clean_up_post_run
from generate_youtube_videos.file_operations import initialize_empty_directories
from generate_youtube_videos.text.generation import generate_youtube_shorts_scripts
from generate_youtube_videos.text.generation import create_video_script_prompts
from generate_youtube_videos.video.operations import segment_video
from generate_youtube_videos.video.operations import fade_and_slice_video
from generate_youtube_videos.video.operations import merge_audio_video
from generate_youtube_videos.video.operations import burn_subtitles_into_video
from generate_youtube_videos.audio.generation import generate_raw_audio_files
from generate_youtube_videos.audio.operations import get_audio_duration
from generate_youtube_videos.audio.operations import generate_subtitle_file_ass
from generate_youtube_videos.audio.operations import transcribe
from icecream import ic
import os
import random

# Need to run:
# export PYTHONPATH="/Users/paulfentress/Desktop/jelly_fish/Jellyfish-Videos:$PYTHONPATH"
# For imports to work.


def add_subtitles_to_video(
        audio: str,
        video: str,
        inference_id: str,
        subtitles_dir: str,
        videos_with_subtitles_dir: str) -> str:
    """DESCRIPTION:
    Adds subtitles to a video including doing the transcription, 
    creating a subtitle file in ASS format, then burning the subtitles
    into the video.

    ARGS:
    - audio (str): The path to the raw audio file.
    - video (str): The path to the merged and sliced video.
    - inference_id (str): The id that connects data in pipeline.
    - output_dir (str): The path to the videos with subtitles dir.

    RETURNS:
    video_with_subtitles (str): The path to the video with subtitles.
    """

    language, segments = transcribe(audio)

    subtitles = generate_subtitle_file_ass(
        language=language,
        inference_id=inference_id,
        segments=segments,
        subtitles_dir=subtitles_dir,
    )

    video_with_subtitles = burn_subtitles_into_video(
        video=video,
        subtitles=subtitles,
        videos_with_subtitles_dir=videos_with_subtitles_dir
    )

    return video_with_subtitles


def process_raw_video_and_audio(
    raw_video:    str,
    raw_audio:    str,
    merged_video: str,
    fade_and_sliced_videos:  str,
    subtitles_dir: str,
    videos_with_subtitles_dir: str,
    inference_id: str
):
    """
    DESCRIPTION:
    Adds all FFMPEG processing to a video. Adds data to different 
    folders along the way.
    1. Gets duration of audio.
    2. Merge audio with video.
    3. Fade and slice the video.
    4. Add subtitles to the video.

    ARGS:
    - raw_video (str): Path to a single raw shortened video file.
    - raw_audio (str): Path to a single raw audio file.
    - merged_video (str): Path to save video merged with audio.
    - fade_and_sliced_videos (str): Path to the save the video after 
    fading and slicing is applied.
    - subtitles_dir (str): Path to dir, to store .ASS subtitle files.
    - videos_with_subtitles (str): Path to save the video with 
    subtitles.

    RETURNS:
    (str) "Done"
    """
    # Compute audio length. Used for meta data.
    ic("Compute audio length. Used for meta data.")
    audio_duration = get_audio_duration(raw_audio)
    ic(audio_duration)

    # Merge audio with video.
    ic("Merge audio with video.")
    merged_video_path = merge_audio_video(
        raw_video,
        raw_audio,
        merged_video
    )

    ic(merged_video_path)

    # Fade and slice the video.
    fade_and_sliced_video = fade_and_slice_video(
        merged_video_path,
        fade_and_sliced_videos,
        audio_duration
    )
    ic(fade_and_sliced_video)

    # Add subtitles to the video.
    video_with_subtitles = add_subtitles_to_video(
        audio=raw_audio,
        video=fade_and_sliced_video,
        inference_id=inference_id,
        subtitles_dir=subtitles_dir,
        videos_with_subtitles_dir=videos_with_subtitles_dir
    )
    ic(video_with_subtitles)

    return "Done"


def generate_video_data(
    video_data_dir: str,
    audio_data_dir: str,
    merged_videos_dir: str,
    fade_and_sliced_videos: str,
    subtitles_dir: str,
    videos_with_subtitles_dir: str
) -> str:
    """
    Creates the entire batch of YouTube shorts videos. Iterates over 
    all data and applies all ffmpeg processing to them.

    ARGS:
    - video_data_dir (str): Path to dir of all short raw videos.
    - audio_data_dir (str): Path to dir of all raw audio files.
    - merged_videos_dir (str): Path to dir of all videos merged with 
    audio.
    - fade_and_sliced_videos (str): Path to dir of all videos that have
    fade and sliced applied.
    - videos_with_subtitles: Path to dir to store all videos with 
    subtitles added. This is currently the last processing applied and 
    therefore the final folder, and therefore where the completed 
    videos are stored.

    RETURNS:
    (str) "Done"
    """

    # All the one minute videos.
    video_files = os.listdir(video_data_dir)

    # Inference IDs used to name videos. Important to keep same ID to
    # reference the correct title when uploading.
    inference_ids = [x.replace(".mp3", "") for x in os.listdir(audio_data_dir)]

    # Iterating over every audio transcript.

    for inference_id in inference_ids:
        raw_audio = os.path.join(audio_data_dir, f"{inference_id}.mp3")
        raw_video = os.path.join(video_data_dir, random.choice(video_files))
        merged_video = os.path.join(merged_videos_dir, f"{inference_id}.mp4")
        fade_and_sliced_video = os.path.join(
            fade_and_sliced_videos, f"{inference_id}.mp4")

        # Generating and saving the YouTube video.
        try:
            process_raw_video_and_audio(
                raw_video=raw_video,
                raw_audio=raw_audio,
                merged_video=merged_video,
                fade_and_sliced_videos=fade_and_sliced_video,
                subtitles_dir=subtitles_dir,
                videos_with_subtitles_dir=videos_with_subtitles_dir,
                inference_id=inference_id
            )

        except Exception as e:
            ic(e)
            ic(f"Failed on ID: {inference_id}")

    return "Done"


def pipeline(num_videos_to_generate: int = NUM_VIDEOS_TO_GENERATE) -> bool:
    """DESCRIPTION:
    Generates 1 minute videos about JellyFish. Have not yet tested 
    generating over 100 videos, usually just do small batches of 10, 
    because thats what the YouTube daily upload limit is for new 
    accounts.

    ARGS: 
    - num_videos_to_generate (int): The number of videos to generate.

    RETURNS:
    bool
    """

    # 0. Creating directories for script.
    ic("🪼 0. Creating directories for script.")
    # The long video path will be made into a parameter.
    clean_up_pre_run()
    long_video_path = "/Users/paulfentress/Desktop/long_jellyfish_vid.mp4"
    output_dir = initialize_empty_directories()
    ic(long_video_path)
    ic(output_dir)

    # 1. Cut long video to short videos.
    ic("🪼 1. Cut long video to short videos.")
    video_data_dir = f"{output_dir}/{ONE_MINUTE_VIDEOS}/"
    short_videos = segment_video(long_video_path, video_data_dir)
    ic(short_videos)

    # 2. Generate n prompts.
    ic("🪼 2. Generates num_videos_to_generate prompts.")
    video_script_prompts = create_video_script_prompts(
        num_prompts=num_videos_to_generate)
    ic(video_script_prompts)

    # 3. Generate the scripts by calling API.
    ic("🪼 3. Generate the scripts by calling API.")
    data = generate_youtube_shorts_scripts(video_script_prompts)
    ic(data)

    # 4. Save data locally.
    ic("🪼 4. Save data locally.")
    csv_path = f"{output_dir}/{HISTORY}/{GOOGLE_SHEET_NAME}.csv"
    data.to_csv(csv_path)
    ic(csv_path)

    # 5. Upload script data to Google Sheet.
    ic("🪼 5. Upload script data to Google Sheet.")
    ic("SKIPPING")
    # upload_data_to_google_sheets(data)

    # 6. Create audio files from scripts.
    ic("🪼 6. Create audio files from scripts.")
    audio_path = f"{output_dir}/{RAW_AUDIO}"
    audio_data_dir = generate_raw_audio_files(csv_path, output_dir=audio_path)
    ic(audio_data_dir)

    # 7. Setting up paths for data.
    ic("🪼 7. Setting up paths for data.")
    output_dir = "Jellyfish"
    video_data_dir = f"{output_dir}/{ONE_MINUTE_VIDEOS}/"
    merged_videos_dir = f"{output_dir}/{VIDEOS_MERGED_WITH_AUDIO}/"
    fade_and_slice_videos = f"{output_dir}/{FADED_AND_SLICED_VIDEOS}/"
    audio_data_dir = f"{output_dir}/{RAW_AUDIO}/"
    videos_with_subtitles_dir = f"{output_dir}/{VIDEOS_WITH_SUBTITLES}/"
    subtitles_dir = f"{output_dir}/{SUBTITLES}/"

    # 8. Generate YouTube videos from short videos and audio.
    ic("🪼 8. Generate YouTube videos from short videos and audio. ")
    job_status = generate_video_data(
        video_data_dir=video_data_dir,
        audio_data_dir=audio_data_dir,
        merged_videos_dir=merged_videos_dir,
        fade_and_sliced_videos=fade_and_slice_videos,
        subtitles_dir=subtitles_dir,
        videos_with_subtitles_dir=videos_with_subtitles_dir
    )
    ic(job_status)

    # 9. Cleaning up data.
    # clean_up_post_run()

    return True


def main():
    pipeline()


if __name__ == "__main__":
    main()
