"""
This script is used to generate YouTube shorts using OpenAI Assistants 
API, TTS API, and a long video to be used for background images.

This script generates 100 videos of around 50 - 60 seconds in length, 
as well as titles for the videos. 

Here is an example of the videos that were generated:
https://www.youtube.com/watch?v=CNIapv394yw

The assistant uses facts added to its knowledge base to create 
video transcripts based on a different questions and topics. 

"""
# Icecream used for better ic statements and debugging.
from icecream import ic

# Used for creating subtitles for the video.
from faster_whisper import WhisperModel

# Pandas used to create video script csv and meta data. 
import pandas as pd

# Google Sheets python API. 
import gspread

# Create service account credentials used to upload data to Google 
# Sheets. 
from oauth2client.service_account import ServiceAccountCredentials

# UUID used to generate unique IDs for video scripts. 
import uuid

# Datetime used to generate dates for database.
from datetime import datetime

# Used for formatting the date_time string.
import pytz

# Open AI used for generating video scripts, and text to speech.
import openai
from openai import OpenAI

# OS used for directory actions. 
import os

# Regex used to clean text output from LLM. 
import re

# Time used to time inference. 
import time

# Random used to randomly select a 1 minute video to add with script. 
import random

# Tiktoken used to count the number of tokens used in request, to 
# compute dollar amount of inference. 
import tiktoken

# Json used for unpacking config file and api responses.  
import json

# subprocess used to call ffmpeg using python. 
import subprocess

# Used to format seconds data for subtitles.
import math

# Configs file can be edited to adjust prompts, voices and more. 
with open('configs.json', 'r') as file:
    configs = json.load(file)

with open('secrets.json', 'r') as file:
    secrets = json.load(file)

# Unpacking and assigning configurations.
GPT_VOICES          = configs["GPT_VOICES"]
GPT_BASE_MODEL      = configs["GPT_BASE_MODEL"]
VIDEO_TOPICS        = configs["VIDEO_TOPICS"]
QUESTION_RULES      = configs["QUESTION_RULES"]
QUESTIONS           = configs["QUESTIONS"]
CREATE_TITLE_PROMPT = configs["CREATE_TITLE_PROMPT"]
PRICE_PER_TOKEN     = configs["PRICE_PER_TOKEN"]
SPREADSHEET_ID      = configs["SPREADSHEET_ID"]
GOOGLE_SHEET_NAME   = configs["GOOGLE_SHEET_NAME"]
DESKTOP_PATH        = configs["DESKTOP_PATH"]

# Folder names
RAW_AUDIO = "RAW_AUDIO"
ONE_MINUTE_VIDEOS = "ONE_MINUTE_VIDEOS"
VIDEOS_MERGED_WITH_AUDIO = "VIDEOS_MERGED_WITH_AUDIO"
FADED_AND_SLICED_VIDEOS = "FADED_AND_SLICED_VIDEOS"
VIDEOS_WITH_SUBTITLES = "VIDEOS_WITH_SUBTITLES"
HISTORY = "HISTORY"
SUBTITLES = "SUBTITLES"

# Unpacking secrets.
OPENAI_API_KEY   = secrets["OPENAI_API_KEY"]
GPT_ASSISTANT_ID = secrets["GPT_ASSISTANT_ID"]
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Open AI client used for text generation and audio generation.
OPEN_AI_CLIENT = OpenAI()

# Loading the assistant with domain knowledge already loaded in.
ASSISTANT = OPEN_AI_CLIENT.beta.assistants.retrieve(
    assistant_id = GPT_ASSISTANT_ID
)

# Threads keep track of the assistants conversation.
THREAD = OPEN_AI_CLIENT.beta.threads.create()


def initialize_empty_directories(output_dir=None):
    """
    Multiple directories are created for the pipeline, because the files 
    change from audio, to video, and cannot have these transformations 
    applied in place. 
    """    

    if not output_dir:     
        # If no path passed, then use desktop.
        output_dir = os.path.join(DESKTOP_PATH, GOOGLE_SHEET_NAME)
    
    # Making root dir.
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


def segment_video(
        input_video_path: str, 
        output_dir:       str, 
        segment_duration: int = 60, 
        volume:           int = 1
    ):
    """
    Slices longer video into shorter videos. Use the volume parameter to 
    decrease the volume of the original video (1 is max vol 0 is silent).
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


def create_video_script_prompts(num_prompts: int = 10) -> list:
    """
    Returns: List
    Creates combinations of questions and topics, which are used 
    to generate videos. Will by default create 10 videos. Can create
    up to 100. Have not tested over 100. Currently using 10, because
    thats okay for YouTube daily upload limit.
    """
    
    prompts = []

    topics = VIDEO_TOPICS
    random.shuffle(topics)

    questions = QUESTIONS
    random.shuffle(questions)

    # Looping through each topic and question. 
    for question in questions:
        for topic in topics:
            # Formatting the question and appending the rules
            prompt =\
                question.format(topic=topic) + " " + QUESTION_RULES
            
            prompts.append(prompt)

            # Stopping script when enough prompts are generated.
            if len(prompts) == num_prompts:
                return prompts 

    return prompts


def encoding_getter(encoding_type: str):
    """
    Returns the appropriate encoding based on the given encoding type 
    (either an encoding string or a model name).
    """
    if "k_base" in encoding_type:
        return tiktoken.get_encoding(encoding_type)
    else:
        return tiktoken.encoding_for_model(encoding_type)


def tokenizer(string: str, encoding_type: str) -> list:
    """
    Returns the tokens in a text string using the specified encoding.
    """
    encoding = encoding_getter(encoding_type)
    tokens = encoding.encode(string)
    return tokens


def token_counter(string: str, encoding_type: str) -> int:
    """
    Returns the number of tokens in a text string using the specified 
    encoding.
    """
    num_tokens = len(tokenizer(string, encoding_type))
    return num_tokens


def ask_gpt_jellyfish_expert(question: str):
    """
    Asks the GPT assistant with domain knowledge a quesetion and 
    returns a text response.
    """

    # Creating the message.
    message = OPEN_AI_CLIENT.beta.threads.messages.create(
        thread_id=THREAD.id,
        role="user",
        content=question
    )

    # Running the thread to get chat history.
    run = openai.beta.threads.runs.create(
        thread_id=THREAD.id,
        assistant_id=ASSISTANT.id
    )

    # Waiting for response from thread. 
    while run.status !="completed":
        run = openai.beta.threads.runs.retrieve(
            thread_id=THREAD.id,
            run_id=run.id
        )
        # Only check the status once every 5 seconds.
        ic(run.status)
        time.sleep(5)

    # Extracting messages from thread.
    messages = openai.beta.threads.messages.list(
        thread_id=THREAD.id
    )

    # Getting the latest message from the thread. 
    response = messages.data[0].content[0].text.value

    # Removing the "source" links so they are not spoken outloud.
    pattern = r'\u3010.*?\u3011'
    cleaned_response = re.sub(pattern, '', response)

    return cleaned_response


def create_video_title(video_transcript: str):
    """
    Calls GPT to create a video title based on the video transcript.
    """

    # The user message explains the context.
    system_message = CREATE_TITLE_PROMPT["SYSTEM"]

    # The user message is for the input to the LLM. 
    user_message = CREATE_TITLE_PROMPT["USER"]
    user_message = user_message.format(video_transcript=video_transcript) 
    
    # The full prompt used in the API call.
    video_title_prompt = f"System: {system_message}\nUser: {user_message}"

    # Making the API call
    response = OPEN_AI_CLIENT.chat.completions.create(
        model=GPT_BASE_MODEL,
        temperature=1,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    
    ic(response)

    # Extracting text from API response. 
    formatted_response = response.choices[0].message.content 
    
    # Styling the video title. 
    video_title = f"🪼 {formatted_response} #shorts #jellyfish"  
 
    return video_title, video_title_prompt


def generate_youtube_shorts_scripts(video_script_prompts: list):
    """
    Calling the API to create the scripts data csv and dataframe.
    """

    # Randomly order the scripts. 
    random.shuffle(video_script_prompts)

    # List of dictionaries used to create a csv and dataframe.
    data = []

    
    for video_script_prompt in video_script_prompts:
        
        # Logging the time to make a request from API.
        inference_start_time = time.time()

        # Creating a BQ/Google Sheets date time format. 
        current_datetime = datetime.now(pytz.UTC)
        datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Generating video script, from expert response. 
        video_script = ask_gpt_jellyfish_expert(video_script_prompt)
        
        # Generating video title from video script.
        video_title, video_title_prompt = create_video_title(video_script)
        
        # UUID used across text, audio and videos. 
        inference_id = str(uuid.uuid4())
        
        # Computing inference dollar amount.
        num_tokens_script = token_counter(video_script, GPT_BASE_MODEL)
        num_tokens_script_prompt = token_counter(
            video_script_prompt, 
            GPT_BASE_MODEL
        ) 

        num_tokens_title = token_counter(video_title, GPT_BASE_MODEL)
        num_tokens_title_prompt = token_counter(
            video_title_prompt, 
            GPT_BASE_MODEL
        )

        total_tokens = [
            num_tokens_script, 
            num_tokens_script_prompt, 
            num_tokens_title,
            num_tokens_title_prompt
        ]

        cost_of_tts = len(video_title) * .000015

        cost_of_text_generation = sum(total_tokens) * PRICE_PER_TOKEN

        # Total cost of inference. 
        cost_of_inference = cost_of_tts + cost_of_text_generation
       
        inference_time = time.time() - inference_start_time
        
        # Creating data for CSV. 
        row = {
                "VIDEO_SCRIPT_PROMPT": video_script_prompt,
                "VIDEO_SCRIPT":        video_script,
                "NUM_CHARS_SCRIPT":    len(video_script),
                "NUM_WORDS_SCRIPT":    len(video_script.split(" ")),
                "VIDEO_TITLE_PROMPT":  video_title_prompt,
                "VIDEO_TITLE":         video_title,
                "NUM_CHARS_TITLE":     len(video_title),
                "NUM_WORDS_TITLE":     len(video_title.split(" ")),
                "INFERENCE_ID":        inference_id,
                "GPT_ASSISTANT_ID":    GPT_ASSISTANT_ID,
                "DATE_TIME":           datetime_str, 
                "COST_OF_INFERENCE":   cost_of_inference,
                "GPT_BASE_MODEL":      GPT_BASE_MODEL,
                "INFERENCE_TIME":      inference_time
            } 

        data.append(row)
        
        ic(row) 

    df = pd.DataFrame(data)    
    return df


def upload_data_to_google_sheets(df: pd.DataFrame):
    """
    Loads entire dataframe into Google Sheet worksheet. Make sure to 
    load to a new worksheet, otherwise the previous one may be deleted.
    """

    # Adding scopes required to load data into Google Sheets.
    scope = [
        'https://www.googleapis.com/auth/spreadsheets', 
        'https://www.googleapis.com/auth/drive'
    ]

    # Authenticating service GCP service account. 
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', 
        scope
    )
    
    # Authorizing Google Sheets API.
    client = gspread.authorize(creds)

    # Open the existing spreadsheet by ID
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Add a new worksheet to the existing spreadsheet the exact size 
    # of the dataframe.
    worksheet = spreadsheet.add_worksheet(
        title=GOOGLE_SHEET_NAME, 
        rows=str(df.shape[0]), 
        cols=str(df.shape[1])
    )

    # Upload DataFrame to the new worksheet.
    response = worksheet.update(
        [df.columns.values.tolist()] + df.values.tolist(), 
        value_input_option='USER_ENTERED'
    )
    
    ic(response)


def generate_raw_audio_files(
    script_csv_file: str, 
    output_dir:      str = "raw_audio" 
    ):
    """
    Text to speech generated from the video scripts. Voices are 
    randomly picked from the avaiable from OpenAi.
    """ 

    # Converting csv to dataframe.
    df = pd.read_csv(script_csv_file)

    # Each row represents one video script. 
    for index, row in df.iterrows():
        
        # The text used for TTS.
        video_script = row["VIDEO_SCRIPT"]

        # Inference ID is used to name the audio file.
        inference_id = row["INFERENCE_ID"]
       
        # Randomly choosing a voice.
        voice = random.sample(GPT_VOICES, 1)[0]

        # Running TTS API.
        tts_response = OPEN_AI_CLIENT.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=video_script,
        )

        # Saving data to a file.
        file_path = f"{output_dir}/{inference_id}.mp3"
        tts_response.stream_to_file(file_path)
        ic(f"{file_path} complete.", index + 1)
    return output_dir


def get_audio_duration(audio_path: str):
    """
    Using ffmpeg to get audio duration in seconds.
    """

    # Run the ffprobe command to get the duration of the audio file.
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    ic(command)

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


def merge_audio_video(
        video_path:  str, 
        audio_path:  str, 
        merged_video_path: str
    ):
    """
    Adds audio to a video. Used to add the voice to the silent or 
    quiet video.
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
        fade_duration:     int = 2
    ) -> str:
    """
    Adds a fade to black to the video, and slices the video after fade is 
    complete.

    ARGS:

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
    

def transcribe(audio) -> tuple:
    """Converts audio into text segments.
    Returns (language: str, segments: list)
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
    """Formats time into subtitle format ASS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)
    formatted_time = f"{hours:01d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    return formatted_time


def generate_subtitle_file_ass(language: str, segments, inference_id: str, subtitles_dir: str):
    """Creates and saves the subtitle file in ASS format.
    Returns subtitle file path : str
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
    text += "Style: Default,Skia,12,&H003a98fc,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1\n"
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


def burn_subtitles_into_video(video: str, subtitles: str, videos_with_subtitles_dir: str):
    """
    Burns subtitles into a video file.

    ARGS:
    video (str): The path to the input video file.
    subtitles (str): The path to the ASS subtitle file.
    videos_with_subtitles_dir (str): The directory where the output video will be saved.

    RETURNS:
    str: The path to the output video file with subtitles.
    """
    ic("HERE ATTEMPTING TO BURN SUBTITLES INTO VIDEO")
    # Ensure the output directory exists
    if not os.path.exists(videos_with_subtitles_dir):
        os.makedirs(videos_with_subtitles_dir)

    # Construct the output file path
    output_video_path = os.path.join(videos_with_subtitles_dir, os.path.basename(video))

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


def add_subtitles_to_video(
        audio: str, 
        video: str, 
        inference_id: str,
        subtitles_dir: str,
        videos_with_subtitles_dir: str
    ):
    """Adds subtitles to a video including doing the transcription, 
    creating a subtitle file in ASS format, then burning the subtitles
    into the video.
    
    ARGS:
    audio (str): The path to the raw audio file.
    video (str): The path to the merged and sliced video.
    inference_id (str): The id that connects data in pipeline.
    output_dir (str): The path to the videos with subtitles dir.
    
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
        fade_and_sliced_video = os.path.join(fade_and_sliced_videos, f"{inference_id}.mp4")

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


def clean_up():
    pass


def pipeline():
    """Run the entire script."""

    # # 0. Creating directories for script.
    # ic("🪼 0. Creating directories for script.")
    # # The long video path will be made into a parameter.
    # long_video_path = "/Users/paulfentress/Desktop/long_jellyfish_vid.mp4"
    # output_dir = initialize_empty_directories()
    # ic(long_video_path)
    # ic(output_dir)
    
    # # 1. Cut long video to short videos.
    # ic("🪼 1. Cut long video to short videos.")
    # video_data_dir = f"{output_dir}/{ONE_MINUTE_VIDEOS}/" 
    # short_videos = segment_video(long_video_path, video_data_dir)
    # ic(short_videos)

    # # 2. Generate 10 prompts.
    # ic("🪼 2. Generate 10 prompts.")
    # video_script_prompts = create_video_script_prompts(num_prompts=2)
    # ic(video_script_prompts)
   
    # # 3. Generate the scripts by calling API.
    # ic("🪼 3. Generate the scripts by calling API.")
    # data = generate_youtube_shorts_scripts(video_script_prompts)
    # ic(data)
   
    # # 4. Save data locally.
    # ic("🪼 4. Save data locally.")
    # csv_path = f"{output_dir}/{HISTORY}/{GOOGLE_SHEET_NAME}.csv"
    # data.to_csv(csv_path)
    # ic(csv_path)

    # # 5. Upload script data to Google Sheet.
    # ic("🪼 5. Upload script data to Google Sheet.")
    # ic("SKIPPING")
    # # upload_data_to_google_sheets(data)
   
    # # 6. Create audio files from scripts.
    # ic("🪼 6. Create audio files from scripts.") 
    # audio_path = f"{output_dir}/{RAW_AUDIO}"
    # audio_data_dir = generate_raw_audio_files(csv_path, output_dir=audio_path)
    # ic(audio_data_dir)

    # 7. Setting up paths for data.
    ic("🪼 7. Setting up paths for data.")
    output_dir = "/Users/paulfentress/Desktop/Jellyfish"
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
    clean_up()


def main():
    pipeline()
    # extracted_audio = "/Users/paulfentress/Desktop/Jellyfish/raw_audio/2f5ed3ac-0cf6-441e-a911-de12de506892.mp3"
    # language, segments = transcribe(audio=extracted_audio)
    # subtitle_file = generate_subtitle_file_ass(
    # language=language,
    # segments=segments,
    # audio_file=extracted_audio
    # )
    # ic(subtitle_file)
    # video = "/Users/paulfentress/Desktop/Jellyfish/final_videos/2f5ed3ac-0cf6-441e-a911-de12de506892.mp4"
    # subtitles = "/Users/paulfentress/Desktop/Jellyfish/raw_audio/2f5ed3ac-0cf6-441e-a911-de12de506892.en.ass"
    # output_dir = "/Users/paulfentress/Desktop/Jellyfish/videos_with_subtitles"
    # burn_subtitles_into_video(video=video, subtitles=subtitles, output_dir=output_dir)
    pass


"""
ffmpeg -i '/Users/paulfentress/Desktop/Jellyfish/final_videos/2f5ed3ac-0cf6-441e-a911-de12de506892.mp4' -vf "ass='/Users/paulfentress/Desktop/Jellyfish/raw_audio/2f5ed3ac-0cf6-441e-a911-de12de506892.en.ass'" -c:a copy '/Users/paulfentress/Desktop/Jellyfish/final_videos/output_video_with_styled_subtitles.mp4'

ffmpeg -i '/Users/paulfentress/Desktop/Jellyfish/final_videos/2f5ed3ac-0cf6-441e-a911-de12de506892.mp4' -i '/Users/paulfentress/Desktop/Jellyfish/raw_audio/2f5ed3ac-0cf6-441e-a911-de12de506892.en.srt' -c:v copy -c:a copy -c:s mov_text '/Users/paulfentress/Desktop/Jellyfish/final_videos/video_with_subtitles.mp4'

"""
    

if __name__ == "__main__":
    main()

# f"[0:v]trim=duration={duration},fade=t=out:st={audio_length}:d={fade_duration}:color=black[v]",     
