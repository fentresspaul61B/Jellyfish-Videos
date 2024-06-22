import pandas as pd
import random
from icecream import ic

from configs import OPEN_AI_CLIENT
from configs import GPT_VOICES


def generate_raw_audio_files(
    script_csv_file: str,
    output_dir:      str = "raw_audio"
):
    """DESCRIPTION:
    Text to speech generated from the video scripts. Voices are 
    randomly picked from the avaiable from OpenAi.

    ARGS:
    - script_csv_file (str): Path to video script csv data.
    - output_dir (str): Path to save generated audio.

    RETURNS:
    output_dir (str): Path to where audio is stored.
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
        # TODO: Refactor depcreceated 'stream_to_file' method.
        file_path = f"{output_dir}/{inference_id}.mp3"
        tts_response.stream_to_file(file_path)
        ic(f"{file_path} complete.", index + 1)
    return output_dir
