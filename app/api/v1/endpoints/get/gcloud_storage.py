from google.cloud import storage
from fastapi import HTTPException, APIRouter
import re
from .....core.google_project_config import *
from .....models.models import *
from .....utils.bucket_helpers import *

router = APIRouter()

# Define the endpoints
@router.get("/get_audios_from_user/{id}")
async def get_audios_from_user_id(id: str):
    return await get_audios_from_user(id)

@router.get("/get_audio/{file_id}/{file_extension}")
async def get_audio(file_id: str, file_extension: AudioExtension):
    return await get_audio(file_id, file_extension)

@router.get("/buckets")
async def get_buckets():
    return await get_buckets()

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
    
async def get_buckets():
    # This snippet demonstrates how to list buckets.
    # *NOTE*: Replace the client created below with the client required for your application.
    # Note that the credentials are not specified when constructing the client.
    # Hence, the client library will look for credentials using ADC.
    storage_client = storage.Client(project=cloud_details["project_id"])
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        bucket_name = bucket.name
        print(bucket.name)
    print("Listed all storage buckets.")
    return "Bucket: " + bucket_name