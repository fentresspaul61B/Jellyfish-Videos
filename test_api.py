import requests


def main():
    # URL of your FastAPI server
    url = 'http://127.0.0.1:8000/uploadfile/'

    # Path to the file you want to upload
    file_path = '/Users/paulfentress/Downloads/7eb42d9d-862e-4647-833a-d2f189d252b0.mp4'

    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Define the name of the form field (must match the name defined in FastAPI)
        files = {'file': (file_path, f)}
        
        # Send the POST request to the server
        response = requests.post(url, files=files)

    # Print the response from the server
    print(response.text)


if __name__ == "__main__":
    main()
