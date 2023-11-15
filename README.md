# Jellyfish GPT: Generating Education Video Content About Jellyfish 

[![Watch the video]](https://www.youtube.com/watch?v=-zABWWJjvCc)

## Table of Contents
- [Introduction](#Introduction)
- [Motivation](#Motivation)
- [Implementation](#Implementation)



I am currently stuck trying to deploy the upload youtube API using 
docker and cloud run. 

The main issue, is that I am trying to load secret files into the 
docker container, and into the GCP server, but this is tricky. 

What I have tried:
1. Uploading all local files, as base64 converted jsons as GitHub Actions
secrets. 
2. Uploading all local files in their json format into GitHub actions, getting
incorrect format error. 

So I think what is happening, is that for #1. is that it is trying to read 
a base 64 json string, which is not working. And for #2, The formating is 
incorrect when putting in the raw json to GitHub secrets. 

The purpose of doing all of this, is because the YouTube API requires certain 
permissions, and I do not want to upload the raw credentials files. 

What I have not yet tried: Decoding the base64 json string inside GCP server.
Print out the contents of the JSON (if possible)

{Show video}


