from google.cloud import storage

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage

    Args:
    bucket_name (str): Name of the GCS bucket.
    source_file_name (str): Path to the file to upload.
    destination_blob_name (str): The desired name for your file in the bucket.

    Returns:
    str: GCS URL of the uploaded file
    """
    # Initialize a storage client using your service account key
    storage_client = storage.Client()

    # Get the bucket object
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob and upload the file's content to GCS
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    # The public URL can be used to access the file directly via HTTP
    return f"gs://{bucket_name}/{destination_blob_name}"

# Example usage
if __name__ == "__main__":
    bucket_name = 'videos-with-subtitles'
    source_file_name = '/Users/paulfentress/Desktop/Jellyfish/VIDEOS_WITH_SUBTITLES'
    destination_blob_name = 'destination-filename-in-gcs'

    uploaded_file_url = upload_to_gcs(bucket_name, source_file_name, destination_blob_name)
    print(f"File uploaded to {uploaded_file_url}")
