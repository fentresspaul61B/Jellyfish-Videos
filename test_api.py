import requests


def main():
    # URL of your FastAPI server
    url = 'http://127.0.0.1:8000/uploadfile/'
    

    url = "https://upload-to-youtube-6gnwtnnisa-uc.a.run.app/uploadfile/"
    # Path to the file you want to upload
    file_path = '/Users/paulfentress/Downloads/7eb42d9d-862e-4647-833a-d2f189d252b0.mp4'
    
    bearer_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImY4MzNlOGE3ZmUzZmU0Yjg3ODk0ODIxOWExNjg0YWZhMzczY2E4NmYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiNjE4MTA0NzA4MDU0LTlyOXMxYzRhbGczNmVybGl1Y2hvOXQ1Mm4zMm42ZGdxLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiNjE4MTA0NzA4MDU0LTlyOXMxYzRhbGczNmVybGl1Y2hvOXQ1Mm4zMm42ZGdxLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTA5MDc5OTE2NDkzMzU0ODM4NTc1IiwiZW1haWwiOiJwYXVscy5tbC5wcm9qZWN0c0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6IjJWbF9FdTJHNC1sZ056UTRfOGJYY2ciLCJuYmYiOjE2OTk4NDI4NjYsImlhdCI6MTY5OTg0MzE2NiwiZXhwIjoxNjk5ODQ2NzY2LCJqdGkiOiJmNzNhY2Q1Y2U2MTAzMTQxNjlkMjFmOTBkYmU4MmU1YjQzM2YyMGNiIn0.MDQMuFb4wTdRr7-TZquE-qEzev4YqMp5eV60wcLtFrLSdJASUdQdx66hCR9vxEi_14ClrrccqLMKh2m72VYNA_xI3rAVuSZcpbONhA0HW1sd-MAn98Gtc9f7s4Jf4BTloRsfSXoz228_bVe69rTsZCmvd0VDWA9pxTBtsLg3OJn0ctyfybc3qUSbNnOewVglWwNKnuMtz3ypWCUF-af1lTEvn8IRXC8IabccL4nFyyWzHEZsbrnrBsXeArQM2mfQlShbskNUiOhbjhilEsqzg-crwvvErYGMQ6Od49hvFfnGCMdOJNI6ql5TN2vexcLF_qS1rSACw06vzyPJoT177w'
    # Open the file in binary mode

    with open(file_path, 'rb') as f:
        # Define the name of the form field (must match the name defined in FastAPI)
        files = {'file': (file_path, f)}
        
        headers = {
            'Authorization': f'Bearer {bearer_token}'
        }
        # Send the POST request to the server
        response = requests.post(url, files=files, headers=headers)

    # Print the response from the server
    print(response.text)


if __name__ == "__main__":
    main()
