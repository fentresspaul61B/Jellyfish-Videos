import requests


def main():
    # URL of your FastAPI server
    url = 'http://127.0.0.1:8000/uploadfile/'
    

    url = "https://upload-to-youtube-6gnwtnnisa-uc.a.run.app/uploadfile/"
    # Path to the file you want to upload
    file_path = '/Users/paulfentress/Downloads/7eb42d9d-862e-4647-833a-d2f189d252b0.mp4'
    
   
    bearer_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImY4MzNlOGE3ZmUzZmU0Yjg3ODk0ODIxOWExNjg0YWZhMzczY2E4NmYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiNjE4MTA0NzA4MDU0LTlyOXMxYzRhbGczNmVybGl1Y2hvOXQ1Mm4zMm42ZGdxLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiNjE4MTA0NzA4MDU0LTlyOXMxYzRhbGczNmVybGl1Y2hvOXQ1Mm4zMm42ZGdxLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTA5MDc5OTE2NDkzMzU0ODM4NTc1IiwiZW1haWwiOiJwYXVscy5tbC5wcm9qZWN0c0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6IjJuWjAxTmpBblBTbnNVd1ZGUkQ5c1EiLCJuYmYiOjE2OTk4NTMyMDgsImlhdCI6MTY5OTg1MzUwOCwiZXhwIjoxNjk5ODU3MTA4LCJqdGkiOiJiOTBhOWQ0MzhiNzcxNmMzZGZkZDBjMGJjMmRjZmJlNTcxYzU3ZjExIn0.X6m1HlUbX3RzhxZKETwF_jT6soc00X_uW08gxcja5h9YdJi_87C1Jv8F6IFye0WHxNS73v5Zo59Jv39oPCdxvH-bcjUHU26J20FYfd2Hq4033ZuTLGm2ykJeH2KPO6IpEMCPPutQKsnHh4ANUUQXZDUrB1IkCM40vGpC9bCCv54KES_X9yq1rrPPgc5N-Dlo9UXD170paPzJscFvJGR7n1T9XXmnWWPqC88H7ldDNmUPxDq7bbsTJLw8SNvIUQ0rGw_nIwG9WSgfxRJxz4iacN2bO4NVZOJF7rVrdt6Vxwf4RmzP8XdBkR8WDWZpXcbfuc0mOqXnSJiBape8dM8phw"
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
