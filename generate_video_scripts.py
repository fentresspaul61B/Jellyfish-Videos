"""
This script is used to generate video scripts, titles, and inference ids
and upload them to google sheets. The final function will also return a 
dictionary of IDs as keys, and scripts as values, which can be passed to 
the audio generation component, to generate audio. 
"""
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from openai.types.beta.threads.run_create_params import ToolAssistantToolsCode
import uuid
# Datetime used to generate dates for database.
from datetime import datetime
# Used for formatting the date_time string.
import pytz

import openai

from openai import OpenAI
import os
import re

# Data is store in big query, and GCP cloud strage buckets.
import time
import random

import tiktoken

import json


# Loading data from the JSON file named "configs.json"
with open('configs.json', 'r') as file:
    configs = json.load(file)

# Unpacking and assigning variables
GPT_VOICES          = configs["GPT_VOICES"]
GPT_BASE_MODEL      = configs["GPT_BASE_MODEL"]
VIDEO_TOPICS        = configs["VIDEO_TOPICS"]
QUESTION_RULES      = configs["QUESTION_RULES"]
QUESTIONS           = configs["QUESTIONS"]
CREATE_TITLE_PROMPT = configs["CREATE_TITLE_PROMPT"]
PRICE_PER_TOKEN     = configs["PRICE_PER_TOKEN"]
SPREADSHEET_ID      = configs["SPREADSHEET_ID"]
GOOGLE_SHEET_NAME   = configs["GOOGLE_SHEET_NAME"]


with open('secrets.json', 'r') as file:
    secrets = json.load(file)

OPENAI_API_KEY = secrets["OPENAI_API_KEY"]
GPT_ASSISTANT_ID = secrets["GPT_ASSISTANT_ID"]

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

OPEN_AI_CLIENT = OpenAI()

ASSISTANT = OPEN_AI_CLIENT.beta.assistants.retrieve(assistant_id=GPT_ASSISTANT_ID)
THREAD = OPEN_AI_CLIENT.beta.threads.create()


def create_video_script_prompts():
    # Assuming VIDEO_TOPICS, QUESTIONS, and QUESTION_RULES are global variables
    global VIDEO_TOPICS, QUESTIONS, QUESTION_RULES

    # List to store the results
    result = []

    # Looping through each topic and question format
    for topic in VIDEO_TOPICS:
        for question_format in QUESTIONS:
            # Formatting the question and appending the rules
            question = question_format.format(topic=topic) + " " + QUESTION_RULES
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
    message = OPEN_AI_CLIENT.beta.threads.messages.create(
        thread_id=THREAD.id,
        role="user",
        content=question
    )

    run = openai.beta.threads.runs.create(
        thread_id=THREAD.id,
        assistant_id=ASSISTANT.id
    )

    while run.status !="completed":
        run = openai.beta.threads.runs.retrieve(
            thread_id=THREAD.id,
            run_id=run.id
        )
        print(run.status)

    messages = openai.beta.threads.messages.list(
        thread_id=THREAD.id
    )

    response = messages.data[0].content[0].text.value

    pattern = r'\u3010.*?\u3011'

    cleaned_response = re.sub(pattern, '', response)

    return cleaned_response


def create_video_title(video_transcript):
    # Constructing the prompt
    system_message = CREATE_TITLE_PROMPT["SYSTEM"]
    user_message = CREATE_TITLE_PROMPT["USER"].format(video_transcript=video_transcript)
    
    # The prompt used in the API call
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
    # Constructing the response
    video_title = "🪼 " + response.choices[0].message.content + " #shorts #jellyfish"

    # Returning the response and the prompt
    return video_title, video_title_prompt


def generate_youtube_shorts_scripts(video_script_prompts: list):

    random.shuffle(video_script_prompts)

    data = []

    for video_script_prompt in video_script_prompts:
        
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
        num_tokens_script_prompt = token_counter(video_script_prompt, GPT_BASE_MODEL) 

        num_tokens_title = token_counter(video_title, GPT_BASE_MODEL)
        num_tokens_title_prompt = token_counter(video_title_prompt, GPT_BASE_MODEL)

        total_tokens = [
            num_tokens_script, 
            num_tokens_script_prompt, 
            num_tokens_title,
            num_tokens_title_prompt
        ]
         
        cost_of_inference = sum(total_tokens) * PRICE_PER_TOKEN
       
        inference_time = time.time() - inference_start_time
        
        # Creating data for Google Sheet. 
        data.append(
            {
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
        )
        print(data) 

    df = pd.DataFrame(data)    
    return df


def upload_data_to_google_sheets(df: pd.DataFrame):
    """Credentials JSON is from service account."""

    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    # Open the existing spreadsheet by ID
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Add a new worksheet to the existing spreadsheet
    worksheet = spreadsheet.add_worksheet(title=GOOGLE_SHEET_NAME, rows=str(df.shape[0]), cols=str(df.shape[1]))

    # Upload DataFrame to the new worksheet
    response = worksheet.update([df.columns.values.tolist()] + df.values.tolist(), value_input_option='USER_ENTERED')
    print(response)


def main():
    
    video_script_prompts = create_video_script_prompts()
    
    data = generate_youtube_shorts_scripts(video_script_prompts) 
    
    upload_data_to_google_sheets(data)

if __name__ == "__main__":
    main()

       
