import json
import openai
from openai import OpenAI
import os
from icecream import ic

# Configs file can be edited to adjust prompts, voices and more.
config_path = "video_domains/jellyfish_domain/configs.json"
with open(config_path, 'r') as file:
    configs = json.load(file)

with open('./secrets.json', 'r') as file:
    secrets = json.load(file)

# Unpacking and assigning configurations.
GPT_VOICES = configs["GPT_VOICES"]
GPT_BASE_MODEL = configs["GPT_BASE_MODEL"]
VIDEO_TOPICS = configs["VIDEO_TOPICS"]
QUESTION_RULES = configs["QUESTION_RULES"]
QUESTIONS = configs["QUESTIONS"]
CREATE_TITLE_PROMPT = configs["CREATE_TITLE_PROMPT"]
PRICE_PER_TOKEN = configs["PRICE_PER_TOKEN"]
SPREADSHEET_ID = configs["SPREADSHEET_ID"]
GOOGLE_SHEET_NAME = configs["GOOGLE_SHEET_NAME"]
DESKTOP_PATH = "."

# Folder names
RAW_AUDIO = "RAW_AUDIO"
ONE_MINUTE_VIDEOS = "ONE_MINUTE_VIDEOS"
VIDEOS_MERGED_WITH_AUDIO = "VIDEOS_MERGED_WITH_AUDIO"
FADED_AND_SLICED_VIDEOS = "FADED_AND_SLICED_VIDEOS"
VIDEOS_WITH_SUBTITLES = "VIDEOS_WITH_SUBTITLES"
HISTORY = "HISTORY"
SUBTITLES = "SUBTITLES"
ROOT_DIR = "./Jellyfish"
VIDEO_TITLE_TEMP = 1
NUM_VIDEOS_TO_GENERATE = 2
URL_TO_REDIRECT_TO = "https://www.wildanimalinitiative.org/donate"


# SUBTITLES SETTINGS

# GCP SETTINGS
TEST_DATA_BUCKET_GCP = "test-data-jellyfish"
GCP_PROJECT_ID = "video-generation-404817"
CLICKED_LINK_TOPIC_ID = "CLICKED-LINK"


# Unpacking secrets.
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]
GPT_ASSISTANT_ID = secrets["GPT_ASSISTANT_ID"]
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Open AI client used for text generation and audio generation.
OPEN_AI_CLIENT = OpenAI()

# Loading the assistant with domain knowledge already loaded in.
ASSISTANT = OPEN_AI_CLIENT.beta.assistants.retrieve(
    assistant_id=GPT_ASSISTANT_ID
)

# Threads keep track of the assistants conversation.
THREAD = OPEN_AI_CLIENT.beta.threads.create()


def main():
    ic(CREATE_TITLE_PROMPT)


if __name__ == "__main__":
    main()
