from google.cloud import storage
from fastapi import HTTPException
import requests, re
from ...config.google_project_config import *
from ...models.models import *
from ...utils.bucket_helpers import *

async def get_audio(file_id: str, file_extension: AudioExtension):
    try:
        storage_client = storage.Client(project=cloud_details['project_id'])
        bucket = storage_client.bucket(cloud_details['bucket_name'])

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Define a regex pattern to extract the fileID from the blob name
        pattern = r'date_(.*?)fileID_'

        # Iterate over the blobs to find the one that matches the 'file_id' and has the correct audio extension
        for blob in blobs:
            # Use regex to extract the fileID from the blob name
            match = re.search(pattern, blob.name)
            if match:
                id_in_blob = match.group(1)
                # Check if the extracted fileID matches the 'file_id' and the file has the correct audio extension
                if id_in_blob == file_id and blob.name.endswith(f".{file_extension}"):
                    # Return the public URL of the blob
                    return blob.public_url

        # If no matching audio file is found, raise an HTTPException
        raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_transcript(file_id: str, file_extension: FileExtension):
    try:
        storage_client = storage.Client(project=cloud_details['project_id'])
        bucket = storage_client.bucket(cloud_details['bucket_name'])

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Iterate over the blobs to find the one that contains the 'file_id' in its name
        for blob in blobs:
            # Split the blob name by slash and get the last part
            last_part = blob.name.rsplit('/', 1)[-1]

            # Split the last part by underscore and get the first part
            id_in_blob = last_part.split('_', 1)[0]

            # Check if the id in the blob name matches the 'file_id' and the file has the correct extension
            if id_in_blob == file_id and last_part.endswith(f".{file_extension}"):
                # Get the content of the blob
                response = requests.get(blob.public_url)
                if file_extension == FileExtension.json:
                    # Render the blob.public_url to a JSON object and return it
                    return response.json()
                elif file_extension == FileExtension.txt:
                    # Render the blob.public_url to a transcript_text and return it as a object {"transcript": transcript_text}
                    transcript_text = response.text
                    return {"transcript": transcript_text}

        # If no matching blob is found, return a message saying that there is no such file with that ID
        return {"message": f"No file found with ID {file_id} and extension .{file_extension}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_audios_from_user(id: str):
    try:
        storage_client = storage.Client(project=cloud_details['project_id'])
        bucket = storage_client.bucket(cloud_details['bucket_name'])

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Create a list to store the URLs of the audio files
        audio_urls = []

        # Iterate over the blobs to find the ones that end with the id
        for blob in blobs:
            # Split the blob name by underscore and get the last part before the extension
            id_in_blob = blob.name.rsplit('.', 1)[0].rsplit('_', 1)[-1]

            # Check if the id in the blob name matches the id
            if id_in_blob == id:
                # Add the public URL of the blob to the list
                audio_urls.append(blob.public_url)

        # Return the list of audio URLs
        return {"urls": sort_links_by_datetime(audio_urls)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))