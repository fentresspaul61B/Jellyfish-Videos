"""Generates speech from text in mp3 form using open AI API. Saves audio to an 
output dir. The text is extract from a CSV file. This audio is later merged with
video and subtitles.

Core ideas:
1. Create a single speech API jobs. 
2. Iterate over video scripts csv to make multiple speech API jobs.
3. Run the speech API jobs. 
"""

from types import MappingProxyType
import pandas as pd
import random
from icecream import ic
from generate_youtube_videos.configs import OPEN_AI_CLIENT
from generate_youtube_videos.configs import GPT_VOICES
from dataclasses import dataclass
from typing import Iterable
from typing import Callable
import httpx
from functools import partial
from audio.helpers import first_order_function
from audio.helpers import higher_order_function
# from collections import namedtuple
# from typing import NamedTuple


@dataclass(frozen=True)
class SpeechJob:
    script_csv_file: str
    output_dir: str


@dataclass(frozen=True)
class SpeechApiData:
    model: str
    voice: str
    input: str
    inference_id: str
    speech_job: SpeechJob


@first_order_function
def pick_random_voice(voices: list = GPT_VOICES) -> str:
    """Picks random voice option from openAI voices."""
    return random.sample(voices, 1)[0]


@first_order_function
def get_script_and_id_tuples_from_csv(job: SpeechJob) -> tuple:
    """Gets the video 'scripts' generated by LLM. Scripts are organized in
    tuple pairs by (VIDEO_SCRIPT, INFERENCE_ID)"""
    rows = pd.read_csv(job.script_csv_file).iterrows()
    return tuple((row["VIDEO_SCRIPT"], row["INFERENCE_ID"]) for _, row in rows)


# TODO: Move to a general helpers file (this function could be used anywhere).
@first_order_function
def create_partial_function(function: Callable, *args, **kwargs) -> Callable:
    """A partial function, creates a function with multiple parameters held 
    constant."""
    return partial(function, *args, **kwargs)


# TODO: Move to a general helpers file (this function could be used anywhere).
@first_order_function
def map_with_multiple_args(function: Callable, iter: Iterable) -> tuple:
    """Maps a function with multiple args to an iteratble."""
    return tuple(map(lambda args: function(*args), iter))


@first_order_function
def call_open_ai_tts_api(job: SpeechApiData) -> httpx.Response:
    """Calls open AI API to generate speech, using job dataclass."""
    tts_response = OPEN_AI_CLIENT.audio.speech.create(
        model=job.model,
        voice=job.voice,
        input=job.input
    )
    return tts_response


@first_order_function
def save_open_ai_tts_api_response_to_mp3(
        job: SpeechApiData, api_response: httpx.Response) -> str:
    """Saves speech audio data to file."""
    file_path = f"{job.speech_job.output_dir}/{job.inference_id}.mp3"
    api_response.stream_to_file(file_path)
    return file_path


@higher_order_function
def create_open_ai_api_tts_job(
        job: SpeechJob,
        video_script: str,
        inference_id: str,
        pick_random_voice: Callable = pick_random_voice) -> SpeechApiData:
    """Creates an API job dataclass, which is used to call OpenAI API."""
    job = SpeechApiData(
        model="tts-1",
        voice=pick_random_voice(),
        input=video_script,
        inference_id=inference_id,
        speech_job=job
    )
    return job


@higher_order_function
def create_open_ai_api_tts_jobs(
        job: SpeechJob,
        get_scripts: Callable = get_script_and_id_tuples_from_csv,
        create_partial_function: Callable = create_partial_function,
        create_api_job: Callable = create_open_ai_api_tts_job,
        map_with_multiple_args: Callable = map_with_multiple_args,
        pick_random_voice: Callable = pick_random_voice) -> tuple:
    """Creates a tuple of API jobs, to generate audio from OpenAI API."""
    create_job_partial = create_partial_function(
        create_api_job,
        job,
        pick_random_voice=pick_random_voice
    )
    return map_with_multiple_args(create_job_partial, get_scripts(job))


@higher_order_function
def run_open_ai_api_tts_job_and_save_to_mp3(
        job: SpeechApiData,
        save_to_file: Callable = save_open_ai_tts_api_response_to_mp3,
        call_api: Callable = call_open_ai_tts_api) -> str:
    """Calls speech api, and saves response to file as mp3."""
    return save_to_file(job, call_api(job))


# Using an immutable dictionary to keep data frozen.
GENERATE_AUDIO_FUNCTIONS = MappingProxyType(
    {
        "GET_SCRIPTS": get_script_and_id_tuples_from_csv,
        "CREATE_API_JOB": create_open_ai_api_tts_job,
        "MAP_WITH_MULTIPLE_ARGS": map_with_multiple_args,
        "PICK_RANDOM_VOICE": pick_random_voice,
        "GENERATE_SPEECH": run_open_ai_api_tts_job_and_save_to_mp3,
        "CREATE_API_JOBS": create_open_ai_api_tts_jobs,
        "CREATE_PARTIAL_FUNCTION": create_partial_function,
        "SAVE_SPEECH_TO_FILE": save_open_ai_tts_api_response_to_mp3,
        "CALL_API": call_open_ai_tts_api
    }
)


# TODO: Rename. compose_generate_speech_func. Is this function adding anything
# or is it just a passthrough function?
@higher_order_function
def compose_generate_speech(
        functions: MappingProxyType = GENERATE_AUDIO_FUNCTIONS) -> partial:
    """Composes the generate speech partial functio."""
    partial_func: partial = functions["CREATE_PARTIAL_FUNCTION"](
        functions["GENERATE_SPEECH"],
        save_to_file=functions["SAVE_SPEECH_TO_FILE"],
        call_api=functions["CALL_API"]
    )
    return partial_func


# TODO: Rename. compose_create_api_jobs_func. Is this function adding anything
# or is it just a passthrough function?
@higher_order_function
def compose_create_api_jobs(
        functions: MappingProxyType = GENERATE_AUDIO_FUNCTIONS) -> partial:
    """Composes the create api jobs partial function."""
    partial_func: partial = functions["CREATE_PARTIAL_FUNCTION"](
        functions["CREATE_API_JOBS"],
        get_scripts=functions["GET_SCRIPTS"],
        create_partial_function=functions["CREATE_PARTIAL_FUNCTION"],
        create_api_job=functions["CREATE_API_JOB"],
        map_with_multiple_args=functions["MAP_WITH_MULTIPLE_ARGS"],
        pick_random_voice=functions["PICK_RANDOM_VOICE"]
    )
    return partial_func


# TODO: Rename? I am not sure if it is obvious enough, that all the code leading
# up to this point, lead to this one core function.
@higher_order_function
def generate_raw_audio_files(
        job: SpeechApiData,
        generate_speech_func: Callable = compose_generate_speech,
        create_api_jobs_func: Callable = compose_create_api_jobs) -> str:
    """Generates speech from the text in csv. Saves audio to output dir."""
    tuple(map(generate_speech_func(), create_api_jobs_func()(job)))
    return job.output_dir


def main():
    # ic(tuple(map(create_api_job, get_script_and_id_tuples_from_csv())))
    pass


if __name__ == "__main__":
    main()


# TODO: Explain the intention and purpose of this abstraction. I think it may be
# confusing that there are two dataclasses that are both considered jobs, but
# one is meant to be iterated over and other is held static.


# TODO: This could be broken down into two functions. The first one is just
# getting the rows from a csv file. The second would be specific to this context
# which is to format them into an iterable used for generating speech. But does
# that abstraction add anything? Its hard to say. Maybe if I need to do that
# action again somewhere else its worth it. But if its only ever done once, then
# its not.


# # TODO: Rename. This name is not specific enough. create_open_ai_tts_job.
# @higher_order_function
# def create_api_job(
#         job: SpeechJob,
#         video_script: str,
#         inference_id: str,
#         pick_random_voice: Callable = pick_random_voice) -> SpeechApiData:
#     """Creates an API job dataclass, which is used to call OpenAI API."""
#     job = SpeechApiData(
#         model="tts-1",
#         voice=pick_random_voice(),
#         input=video_script,
#         inference_id=inference_id,
#         speech_job=job
#     )
#     return job
