from pygments import highlight, lexers, formatters
from fastapi import HTTPException
import json, os, requests
from ..core.google_project_config import *
from .bucket_helpers import upload_file_to_bucket
from .save_file import save_audio

def pretty_print_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, 
        lexers.JsonLexer(), 
        formatters.TerminalFormatter()
    )
    # print(colorful_json)
    return colorful_json

# Helper function for getting audio file path
def get_file_path(full_url):
    base_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/"
    # Remove the base URL
    audio_path = full_url.replace(base_url, "")
    return audio_path

def rm_local_file(file_path):
    if file_path is not None:
        try:
            os.remove(file_path)
            print(f"Successfully removed {file_path}")
        except Exception as e:
            print(f"Error while trying to remove {file_path}: {e}")
    else:
        print("No file path provided, skipping removal.")

async def encode_audio_filename(user_id: str, file_name: str):
    try:
        file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{file_name}"
        # Initialize file_path before the if statement
        file_path = os.path.join("audios", file_url.split("/")[-1])

        response = requests.get(file_url, stream=True)

        if response.status_code == 200:
            # Open the local file in write mode
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"File downloaded successfully to {file_path}")

            audio_file = save_audio(file_path, user_id)
            print(audio_file)
            upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], audio_file['new_file_name'], audio_file['new_file_name'])

            rm_local_file(audio_file["new_file_name"])

            return {
                "new_file_name": audio_file['new_file_name'], 
                "file_id": audio_file['file_id']
            }
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            # Handle the case where the file could not be downloaded
            raise Exception(f"Failed to download file. Status code: {response.status_code}")

    except Exception as e:
        # Rethrow the exception to be caught by the calling function
        raise e
    
