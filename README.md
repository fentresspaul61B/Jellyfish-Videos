# Jellyfish GPT 

![alt text](youtube.gif)

[[Checkout the YouTube Channel!]](https://www.youtube.com/watch?v=-zABWWJjvCc)
--- 
## AI Generated Educational Video Content About Jellyfish 
This project uses FFPMEG, OpenAI Assistants, and OpenAI TTS to create short educational videos about jellyfish. The purpose of purpose of this project is to explore how to quickly generate batches of high quality and factual content using an OpenAI assistant with a knowledge base, which can be used for educational purposes. 

--- 

## Table of Contents
- [Files](#files)
- [Implementation](#implementation)
- [Sources](#sources)
--- 


## Files 

### configs.json 
Configs file that contains variables like prompts, filepaths, and model settings. 

### generate_youtube_videos.py 
Main script that has all functions to generate short form video content using OpenAI agents. 

### jellyfish_facts.txt
Factual information from the web, about jellyfish, used for the agents knowledge base. 



## Example
This is how the video scripts are created:

### Add Data to Knowledge base. 
Ask the jellyfish expert:
> Can you briefly explain the reproduction of jellyfish? If information is not contained in the document, skip the question, and explain something you do know. Do not say what information is or is not contained in the document provided. Keep your response concise, and less than 100 words.

Expert response:
> "Jellyfish reproduction is fascinating! They have a two-stage life cycle: the polyp stage and the medusa stage. In the polyp stage, they can reproduce asexually by budding, which is like cloning. However, when they are mature jellyfish, or medusae, they reproduce sexually by releasing eggs and sperm into the water to create larval jellyfish called planulae. These planulae then settle on a surface and grow into new polyps, starting the cycle all over again. Nature's pretty amazing, right?"

Video Title: 
> 🪼 "Understanding the Two-Stage Reproduction Cycle of Jellyfish" #shorts #jellyfish

Video result:


## Sources
These are the sources used to create the knowledge base, used to ensure factual information in the videos.
 
- https://www.montereybayaquarium.org/animals/animals-a-to-z/jellies?gclid=CjwKCAiA6byqBhAWEiwAnGCA4IPlxw4o3J9X3A-D4msmsEMHDF2z-DdQIZY5xrXtyn7b6XkGlYsLiRoC7d4QAvD_BwE
- https://www.mbari.org/news/
- https://www.mbari.org/animal/bloody-belly-comb-jelly/
- https://www.mbari.org/news/how-comb-jellies-adapted-to-life-in-the-deep-sea/
- https://www.mbari.org/news/ctenophores-the-story-of-evolution-in-the-oceans/
- https://ocean.si.edu/ocean-life/invertebrates/jellyfish-and-comb-jellies#section_16508



