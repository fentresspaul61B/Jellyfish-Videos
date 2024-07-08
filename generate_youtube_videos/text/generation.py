import random
import tiktoken
from icecream import ic
import pandas as pd
import re
import time
from datetime import datetime
import pytz
import uuid
import openai
from configs import VIDEO_TOPICS
from configs import QUESTIONS
from configs import QUESTION_RULES
from configs import OPEN_AI_CLIENT
from configs import THREAD
from configs import ASSISTANT
from configs import CREATE_TITLE_PROMPT
from configs import GPT_BASE_MODEL
from configs import VIDEO_TITLE_TEMP
from configs import GPT_ASSISTANT_ID
from configs import PRICE_PER_TOKEN


# TODO: Refactor (break into smaller functions)
def create_video_script_prompts(num_prompts: int = 10) -> list:
    """DESCRIPTION:
    Creates combinations of questions and topics, which are used 
    to generate videos. Will by default create 10 videos. Can create
    up to 100. Have not tested over 100. Currently using 10, because
    thats okay for YouTube daily upload limit.

    ARGS:
    - num_prompts (int): Number of prompts to create.

    RETURNS:
    prompts: list
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
    """DESCRIPTION:
    Returns the appropriate encoding based on the given encoding type 
    (either an encoding string or a model name). Used for calculating
    inference cost.

    ARGS:
    - encoding_type (str): Encoded string or model name.

    RETURNS:
    Encoding object.
    """
    if "k_base" in encoding_type:
        return tiktoken.get_encoding(encoding_type)
    else:
        return tiktoken.encoding_for_model(encoding_type)


def tokenizer(string: str, encoding_type: str) -> list:
    """DESCRIPTION:
    Returns the tokens in a text string using the specified encoding.

    ARGS:
    - string (str): Input text to tokenize.
    - encoding_type: (str): Encoding type for tokenizer.

    RETURNS:
    tokens
    """

    encoding = encoding_getter(encoding_type)
    tokens = encoding.encode(string)
    return tokens


def token_counter(string: str, encoding_type: str) -> int:
    """DESCRIPTION:
    Returns the number of tokens in a text string using the specified 
    encoding.

    ARGS:
    - string (str): String to count tokens from.
    - encoding_type: (str): Encoding type for tokenizer.

    RETURNS:
    num_tokens (int)
    """
    num_tokens = len(tokenizer(string, encoding_type))
    return num_tokens


def ask_gpt_jellyfish_expert(question: str) -> str:
    """DESCRIPTION:
    Asks the GPT assistant with domain knowledge a quesetion and 
    returns a text response.

    ARGS:
    - question (str): Question to ask GPT with knowledge base.

    RETURNS:
    cleaned_response (str): Answer from GPT that has been cleaned.
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
    while run.status != "completed":
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


def create_video_title(video_transcript: str) -> tuple:
    """DESCRIPTION
    Calls GPT to create a video title based on the video transcript.

    ARGS:
    - video_transcript (str): Generated script for video.

    RETURNS:
    (video_title: str, video_title_prompt: str)
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
        temperature=VIDEO_TITLE_TEMP,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    ic(response)

    # Extracting text from API response.
    formatted_response = response.choices[0].message.content

    # Styling the video title. 🪼
    video_title = f"{formatted_response} #shorts #jellyfish"

    return video_title, video_title_prompt


def generate_youtube_shorts_scripts(video_script_prompts: list) -> pd.DataFrame:
    """DESCRIPTION:
    Calling the API to create the scripts data csv and dataframe.

    ARGS:
    - video_script_prompts (list): All prompts used to create video scripts.

    RETURNS:
    df (pd.DataFrame): A dataframe containing scripts, and meta data.
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
