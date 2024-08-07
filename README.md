# 🪼 Jellyfish GPT 

![example workflow](https://github.com/fentresspaul61B/Jellyfish-Videos/actions/workflows/run_tests.yml/badge.svg)

![alt text](docs/images/jellyfish.gif)

## AI Generated Educational Video Content About Jellyfish 
This project uses FFPMEG, OpenAI Assistants, and OpenAI TTS to create short educational videos about jellyfish. The purpose of purpose of this project is to explore how to quickly generate batches of high quality and factual content using an OpenAI assistant with a knowledge base, which can be used for educational purposes. 

I plan on creating more YouTube channels and content for educational purposes, as well as to raise awareness and even donations for causes that I care about. 
[[Checkout the YouTube Channel!]](https://www.youtube.com/watch?v=-zABWWJjvCc)

## Table of Contents
- [Files](#files)
- [Implementation](#implementation)  
- [Sources](#sources)
- [Motivation](#motivation)

## Files 

### configs.json 
Configs file that contains variables like prompts, filepaths, and model settings. 

### generate_youtube_videos.py 
Main script that has all functions to generate short form video content using OpenAI agents. 

### jellyfish_facts.txt
Factual information from the web, about jellyfish, used for the agents knowledge base. 


---
## Implementation


<img src="docs/images/script_diagram.png" alt="alt text" width="700"/>

### Step #1: Add data to knowledge base
In order to create content that is based on facts and avoid LLM hallucinations, factual scientific information from the web is utilized to create a knowledge base for the agent.  This knowledge base is stored in a text file. Below is a snippet from the knowledge base:

> "Jellies play a vital role in ocean ecosystems. Not only do they eat plankton, but some are food for large animals like sea turtles. In Monterey Bay, for example, the enormous Pacific leatherback sea turtle travels across the Pacific Ocean, all the way from Indonesia, to feed specifically on sea nettles.
A recent study led by the Aquarium showed that jellies are also threatened by microplastics, and that they serve as an entry point for microplastics in the open ocean food chain. This shows how important jellies are as a food source for many animals."

### Step #2: Find a long and publicly available youtube video
Find a long video that is available to use freely. This longer video will serve as a background for the short videos we are creating. 

### Step #3: Slice long videos into shorter videos
FFMPEG was used to slice a longer video into shorter ones, as well as decrease or mute the volume of the original video. 

### Step #4: Generate video scripts, titles and metadata
Next step is to create YouTube scripts and titles using our OpenAI agent. The script is later converted to audio, to create the narration for the video. OpenAI API assistants were used to generate the text, and well as the Google Sheets API to store the metadata. The reason I chose to use Google Sheets, and not a database, is because it is easier to copy data from a google sheet into the YouTube UI. (I would automate the uploading of the YouTube videos; however, YouTube will block videos uploaded via the API). 

#### Metadata
| Column Name         | Description          |
|---------------------|----------------------|
| VIDEO_SCRIPT_PROMPT | The prompt used to generate the video script        |
| VIDEO_SCRIPT        | The actual script of the video        |
| NUM_CHARS_SCRIPT    | Number of text characters in script        |
| NUM_WORDS_SCRIPT    | Number of words in script        |
| VIDEO_TITLE_PROMPT  | Prompt to generate title       |
| VIDEO_TITLE         | The generated title       |
| NUM_CHARS_TITLE     | Number of text characters in title        |
| NUM_WORDS_TITLE     | Number of words in title        |
| INFERENCE_ID        | A unique ID used to keep track of text, video, and audio files used for the same video       |
| GPT_ASSISTANT_ID    | ID to pull jellyfish assistant       |
| DATE_TIME           | Timestamp       |
| COST_OF_INFERENCE   | Calculated total cost of inference in dollars, including text and audio generation       |
| GPT_BASE_MODEL      | Model used       |
| INFERENCE_TIME      | Time for text generation start to finish        |

Metadata about the inference turned out to be useful when experimenting with prompts, which is something I learned from my job. 

#### Example of prompts
Script Prompt:
> Can you briefly explain the reproduction of jellyfish? If information is not contained in the document, skip the question, and explain something you do know. Do not say what information is or is not contained in the document provided. Keep your response concise, and less than 150 words.

Response:
> "Jellyfish reproduction is fascinating! They have a two-stage life cycle: the polyp stage and the medusa stage. In the polyp stage, they can reproduce asexually by budding, which is like cloning. However, when they are mature jellyfish, or medusae, they reproduce sexually by releasing eggs and sperm into the water to create larval jellyfish called planulae. These planulae then settle on a surface and grow into new polyps, starting the cycle all over again. Nature's pretty amazing, right?"

Title Prompt: 
>"System: You are a helpful assistant who creates youtube video titles. Only return the one YouTube title, and nothing else, based on the video transcript. Keep the length of the title less than 80 characters.
User: {Transcript}

Response (After adding emojis and hashtags):
> 🪼 "Understanding the Two-Stage Reproduction Cycle of Jellyfish" #shorts #jellyfish

### Step #5: Generate audio data
Once the video scripts are complete in text format, the audio is generated from the text, and saved to a directory.

### Step #6: Merge and edit short videos with audio using FFMPEG 
Short videos are merged, trimmed, cropped, and faded using FFMPEG. A one minute background video is randomly selected from the batch, and merged with the audio iteratively.

![alt text](docs/images/generated_videos_in_dir.png)

### Step #7: Upload videos to YouTube
There is now 2 main components to upload the videos: 
1. The Google Sheet: Used to copy and paste video title into YouTube UI
2. Directory of final videos.

![alt text](docs/images/youtube.gif)


## Sources
These are the sources used to create the knowledge base, used to ensure factual information in the videos.
 
- https://www.montereybayaquarium.org/animals/animals-a-to-z/jellies?gclid=CjwKCAiA6byqBhAWEiwAnGCA4IPlxw4o3J9X3A-D4msmsEMHDF2z-DdQIZY5xrXtyn7b6XkGlYsLiRoC7d4QAvD_BwE
- https://www.mbari.org/news/
- https://www.mbari.org/animal/bloody-belly-comb-jelly/
- https://www.mbari.org/news/how-comb-jellies-adapted-to-life-in-the-deep-sea/
- https://www.mbari.org/news/ctenophores-the-story-of-evolution-in-the-oceans/
- https://ocean.si.edu/ocean-life/invertebrates/jellyfish-and-comb-jellies#section_16508

## Motivation
The purpose of this project is to share interesting facts about jellyfish for entertainment and educational purposes. If you love wild animals like jellyfish too, please donate to the wild animal initiative, which seeks to reduce harm caused to animals in the wild. 

https://www.wildanimalinitiative.org/donate 

[More code clean up coming soon]

# TODO

## Steps for Building Project
1. Clone the project from GitHub.
2. Create a new venv: ```python -m venv venv```
3. Start the new venv: ``` source venv/bin/activate```
4. Upgrade pip: ```pip install --upgrade pip```
5. Install packages: ```pip install -r requirements.txt```
6. Create new secrets file: ```touch secrets.json```
7. Add ```OPENAI_API_KEY```
8. Add: ```GPT_ASSISTANT_ID```
9. Download long video of Jellyfish: https://drive.google.com/file/d/
13Bp01kgVvuJHAyqfseFeBP-MLUk7YOTl/view?usp=drive_link (I will make this script more generalized one day to work for any video?)
10. Install FFMPEG ```sudo apt-get install ffmpeg``` or ```brew install ffmpeg```

## Turn entire script into bash command
I want to be able to copy and paste some code into the terminal, and 
it will do everything from pulling the code from GitHub, create the 
folders, generate the videos, open all the windows, log into YouTube,
upload all the videos, close the windows, delete the folders and send
a report file to me through email?

Think

Run the script in GCP cloud run.

Have the scripts 

https://www.digitalocean.com/community/tutorials/how-to-generate-and-add-subtitles-to-videos-using-python-openai-whisper-and-ffmpeg

Issue:
Images of video files are selected based on probability and similarity
to reference video, not on inference id, so need to figure out a way
to sync the reference ID, with the process of dragging, and dropping
the video.

Use Infrastructure as code, so when the script is generalized, I can spin up 
multiple different video generators, on different servers. 

TODO: Need to deploy redirect service, in order to get a redirect URL. 
Then add the logic into the pipeline to add dynmically add the redirect
URL to the description.


No Side Effects: The function does not modify any external state or variables.
Deterministic: The function returns the same output given the same input.
No I/O Operations: The function does not perform any input/output operations such as reading from or writing to disk, or making network requests.



Hire Order Functions:
Separating concerns: Decouples fetching and processing logic.
Improving testability: Makes it easier to inject mock functions for testing.
Isolating side effects: Keeps the core logic pure and unaware of side effects.
Promoting reusability and composition: Allows easy swapping of different implementations.


## Examples
```python
# Incorrect Example:
@log_data
def pick_random_voice() -> str:
    """Picks random voice option from openAI voices."""
    return random.sample(GPT_VOICES, 1)[0]


@log_data
def create_api_job(job: SpeechJob, video_script: str, inference_id: str) -> SpeechApiData:
    """Creates an API job dataclass, which is used to call OpenAI API."""
    job = SpeechApiData(
        model="tts-1",
        # function is called directly inside.
        voice=pick_random_voice(), 
        input=video_script,
        inference_id=inference_id,
        speech_job=job
    )
    return job


# Correct Example:
@log_data
def pick_random_voice() -> str:
    """Picks random voice option from openAI voices."""
    return random.sample(GPT_VOICES, 1)[0]


@log_data
def create_api_job(job: SpeechJob, video_script: str, inference_id: str, 
voice_pick_function: Callable) -> SpeechApiData:
    """Creates an API job dataclass, which is used to call OpenAI API."""
    job = SpeechApiData(
        model="tts-1",
        # Function is instead an interchangeable parameter.
        voice=voice_pick_function(),
        input=video_script,
        inference_id=inference_id,
        speech_job=job
    )
    return job
```

This can be extanded by making immutable data objects (like named tuples) as arguments into other functions, which contain a number of functions, which can be used to compose more complex higher order functions.

For each file it should roughly follow this pattern. 
1. Define all the first order functions at the top of the file (those which do not call, accept, or return other functions). 
2. Create a function bundle or some type of immutable pbject containing the first order functions.
3. Define any higher order functions, using the function bundle as an argument where needed.

Dev process:
1. Start by writing monolithic file with functions which may be long, just to get an initial program working. 
2. Start breaking the functions down into smaller functions where ever possible, and use those functions within other functions. 
3. Seperate files if files are growing to long or complicated. 
4. Seperate the first order functions from the higher order functions. 
5. Create first order function groupings, which can be passed and used in the higher order functions. 
6. Seperate out functions which are very general, to some type of utils or helper directory, such that they can be re used across the program. 
7. Keep iterating over this process until all complex logic is composed of multiple swappable componoent functions. 
8. Make sure to be writing tests for all functions along the way. 
9. Observe the function input parameters which are unchagning and used throughout the functions in order to build the final result. Try to encapsulate these together in some type of dataclass or object, to pass throughout the program. 

Ideally, all of the higher order functions would take the parameters function object, and the function bundle. These two abstractions should encapsulate all the need functionality and information to complete the task. 


