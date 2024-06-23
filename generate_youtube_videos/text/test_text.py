"""

"""
import pandas as pd
from icecream import ic
from generate_youtube_videos.text.generation import create_video_script_prompts
from generate_youtube_videos.text.generation import encoding_getter
from generate_youtube_videos.text.generation import tokenizer
from generate_youtube_videos.text.generation import token_counter
from generate_youtube_videos.text.generation import ask_gpt_jellyfish_expert
from generate_youtube_videos.text.generation import create_video_title
from generate_youtube_videos.text.generation import generate_youtube_shorts_scripts
from configs import GPT_BASE_MODEL


def test_create_video_script_prompts() -> None:
    """DESCRIPTION:
    Tests creating prompt combinations. Prompts are different hard 
    coded combinations of topics, and questions. There is a finite 
    amount of prompts. What creates the randomness, is mostly from 
    using a high temp on the base LLM to create more variation for 
    similar inputs.

    ARGS: None

    RETURNS: None

    """

    # Simple test case of making 1 prompt.
    prompts = create_video_script_prompts(1)
    message = "Making 1 prompt failed."
    assert len(prompts) == 1, message

    # testing default of 10.
    prompts = create_video_script_prompts()
    message = "Using default of 10 failed."
    assert len(prompts) == 10, message

    # testing 100.
    prompts = create_video_script_prompts(100)
    message = "Creating 100 prompts failed."
    assert len(prompts) == 100, message

    # Anything past 112 fails, because there is a finite amount of
    # combinations.


def test_encoding_getter() -> None:
    """DESCRIPTION:

    ARGS: None

    RETURNS: None
    """
    encoder = encoding_getter(GPT_BASE_MODEL)
    message = "Getting encoder for GPT 4 failed."
    assert encoding_getter(GPT_BASE_MODEL), message
    pass


def test_tokenizer() -> None:
    """DESCRIPTION:

    ARGS:

    RETURNS
    """
    test_string = "My test string!"
    tokens = tokenizer(test_string, GPT_BASE_MODEL)
    message = "Result is not a list."
    assert isinstance(tokens, list), message


def test_token_counter() -> None:
    """DESCRIPTION:

    ARGS: None

    RETURNS: None
    """
    test_string = "My test string!"
    num_tokens = token_counter(test_string, GPT_BASE_MODEL)
    message = "Result is not an int."
    assert isinstance(num_tokens, int), message
    message = "Num tokens is not greater than 0."
    assert num_tokens > 0, message


def test_ask_gpt_jellyfish_expert() -> None:
    """DESCRIPTION:

    ARGS: None

    RETURNS: None
    """
    prompts = create_video_script_prompts(2)
    responses = []
    for prompt in prompts:
        response = ask_gpt_jellyfish_expert(prompt)
        responses.append(response)
        message = "Response is not of type str."
        assert isinstance(response, str), message
    message = "Asked two questions, but did not get back 2 answers."
    assert len(responses) == 2, message


def test_create_video_title() -> None:
    """DESCRIPTION:

    ARGS:

    RETURNS:
    """
    script = create_video_script_prompts(1)
    video_title, video_title_prompt = create_video_title(script)

    message = "Video title is not of type str."
    assert isinstance(video_title, str), message

    message = "Video is over 100 characters."
    assert len(video_title) <= 100, message


def test_generate_youtube_shorts_scripts() -> None:
    """DESCRIPTION:

    ARGS:

    RETURNS:
    """
    prompts = create_video_script_prompts(5)
    df: pd.DataFrame = generate_youtube_shorts_scripts(prompts)
    assert isinstance(df, pd.DataFrame)

    video_scripts: pd.Series = df["VIDEO_SCRIPT"]
    ic(video_scripts)
    message: str = "Video scripts have duplicates."
    assert len(set(video_scripts)) == len(video_scripts), message

    # There should be no missing values in the table.
    has_missing_values: bool = df.isna().any().any()
    message: str = "Data is missing from the df."
    assert not has_missing_values, message


def main():
    test_generate_youtube_shorts_scripts()
    pass


if __name__ == "__main__":
    main()
