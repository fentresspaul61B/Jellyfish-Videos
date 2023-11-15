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


def segment_video(
        input_video_path: str, 
        output_dir:       str, 
        segment_duration: int =60, 
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
        command.append('-c:a', 'copy')  

    # Creating the file names. These file names do not need a special ID 
    # because they are randomly selected to create videos.
    command.append(os.path.join(output_dir, 'jelly_fish_%03d.mp4'))

    # Execute the command.
    subprocess.run(command, check=True)

    return output_dir


def create_video_script_prompts():
    """
    Creates combinations of questions and topics, which are used 
    to generate videos.
    """
    
    result = []

    # Looping through each topic and question. 
    for topic in VIDEO_TOPICS:
        for question_format in QUESTIONS:
            # Formatting the question and appending the rules
            question =\
                question_format.format(topic=topic) + " " + QUESTION_RULES
            result.append(question)

    return result


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
        print(run.status)

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
    
    print(response)

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
         
        cost_of_inference = sum(total_tokens) * PRICE_PER_TOKEN
       
        inference_time = time.time() - inference_start_time
        
        # Creating data for Google Sheet. 
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
        
        print(row) 

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
    
    print(response)


def generate_raw_audio_files(
    script_csv_file: str, 
    output_dir:      str = "jelly_fish_audio" 
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

    return file_path


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
        output_path: str = 'test_vid.mp4'
    ):
    """
    Adds audio to a video. Used to add the voice to the silent or 
    quiet video.
    """
    
    # Ensure the output directory exists.
    output_dir = os.path.dirname(output_path)
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
        output_path        # path for the output file
    ]

    # Run the FFmpeg command
    result = subprocess.run(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
    )

    # Check if FFmpeg command was successful.
    if result.returncode != 0:
        raise Exception('FFmpeg failed', result.stderr)

    return output_path


def fade_and_slice_video(
        input_video_path:  str, 
        output_video_path: str, 
        audio_length:      str,
        fade_duration:     int = 2
    ):
    """
    Adds a fade to black to the video, and slices the video after fade is 
    complete.
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
        print(f'An error occurred: {e}')
        return None


def process_raw_video_and_audio(
        raw_video:    str, 
        raw_audio:    str, 
        merged_video: str,
        final_video:  str,
        inference_id: str
    ):
    """
    First adds audio to video, then fades and slices the video.
    """
    
    # Compute audio length. 
    audio_duration = get_audio_duration(raw_audio)
    print(audio_duration)

    # Merge audio with video.
    merged_video_path = merge_audio_video(
        raw_video, 
        raw_audio, 
        merged_video
    )

    print(merged_video_path)

    # Fade and slices the video.
    final_video_path = fade_and_slice_video(
        merged_video, 
        final_video, 
        audio_duration
    )

    return "Done"


def generate_video_data(video_data_dir: str, audio_data_dir: str):
    """
    Creates the entire batch of YouTube shorts videos
    """

    # All the one minute videos.
    video_files = os.listdir(video_data_dir)

    # Inference IDs used to name videos. Important to keep same ID to 
    # reference the correct title when uploading.
    inference_ids = [x.replace(".mp3", "") for x in os.listdir(audio_data_dir)]

    # Two folders are required for intermediary processing. 
    os.mkdir("processed_video")
    os.mkdir("processed_video_final")

    # Iterating over every audio transcript.
    for inference_id in inference_ids:
        raw_audio = f"{audio_data_dir}/{inference_id}.mp3"
        raw_video = f"{video_data_dir}/{random.choice(video_files)}"
        merged_video = f"processed_video/{inference_id}.mp4"
        final_video = f"processed_video_final/{inference_id}.mp4"

        # Generating and saving the YouTube video.
        try:
            process_raw_video_and_audio(
                raw_video, 
                raw_audio, 
                merged_video, 
                final_video,
                inference_id
            )
        
        except Exception as e:
            print(e)
            print(f"Failed on ID: {inference_id}")
    
    return "Done"


def main():
    """Run the entire script."""
    
    # 1. Cut long video to short videos. 
    # short_videos = segment_video(long_video_path, output_dir)

    # 2. Generate the prompts.
    # video_script_prompts = create_video_script_prompts()
   
    # 3. Generate the scripts by calling API.
    # data = generate_youtube_shorts_scripts(video_script_prompts) 
   
    # 4. Save data locally.
    # data.to_csv(f"{GOOGLE_SHEET_NAME}.csv")

    # 5. Upload script data to Google Sheet.
    # upload_data_to_google_sheets(data)
   
    # 6. Create audio files from scripts. 
    # audio_dir = generate_raw_audio_files(f"{GOOGLE_SHEET_NAME}.csv") 
   
    # 7. Generate YouTube videos from short videos and audio.   
    # generate_video_data(short_vidoes, audio_dir)


if __name__ == "__main__":
    main()

# f"[0:v]trim=duration={duration},fade=t=out:st={audio_length}:d={fade_duration}:color=black[v]",     
