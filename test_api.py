import requests


def main():
    # URL of your FastAPI server
    url = 'http://127.0.0.1:8000/uploadfile/'
    

    url = "https://upload-to-youtube-6gnwtnnisa-uc.a.run.app/uploadfile/"
    # Path to the file you want to upload
    file_path = '/Users/paulfentress/Downloads/7eb42d9d-862e-4647-833a-d2f189d252b0.mp4'
    
    
    # Open the file in binary mode
    bearer_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImY4MzNlOGE3ZmUzZmU0Yjg3ODk0ODIxOWExNjg0YWZhMzczY2E4NmYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiNjE4MTA0NzA4MDU0LTlyOXMxYzRhbGczNmVybGl1Y2hvOXQ1Mm4zMm42ZGdxLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiNjE4MTA0NzA4MDU0LTlyOXMxYzRhbGczNmVybGl1Y2hvOXQ1Mm4zMm42ZGdxLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTA5MDc5OTE2NDkzMzU0ODM4NTc1IiwiZW1haWwiOiJwYXVscy5tbC5wcm9qZWN0c0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6IjFUaktVaERhTUZ1X3FMVnVCTzVWT0EiLCJuYmYiOjE2OTk4NDkyMDYsImlhdCI6MTY5OTg0OTUwNiwiZXhwIjoxNjk5ODUzMTA2LCJqdGkiOiJkMTZmMGRlNjE1OWMxYzE2OWUzNzNkMjUwZjNhYjQxYmFhYTA2ZjNmIn0.WYWDm5xnSswt6cjEtF69In42XqGYc2hjHThjS-UYIKCoXOFdJlT4VjP5QBZkQmnIcRevfKJq9uyOt5H6pXvX5vJRTAzUAA9dvroLbdxS6bSgxN3Ic2YtU3tKbaj562Nvciwi8Cq14M_YHZ4-rDgy2-ZVSr52h_qRXogB5_KHeF9VLvcBgahzpoHM6vR47mAVhLIaJYaw-62D3ErkWb0N8orpoRjGaVVJjs0CfeOUqC7jqWuRJkVDc7dO-YtuqM_aRaW4LmwvXeDvnpkDFM9H8iIwNrKMm_BTEfsy7QH5js5cmNnQicH1ItEtoVSZsjIXle8ks3LKGyUAWWGBac8-qw"
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
