from pygments import highlight, lexers, formatters
from fastapi import HTTPException
import json, os, requests
from ..config.google_project_config import cloud_details
from ..utils.google_storage import upload_file_to_bucket
from ..utils.save_file import save_audio

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
def extract_audio_path(full_url):
    base_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/"
    # Remove the base URL
    audio_path = full_url.replace(base_url, "")
    return audio_path

def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"Successfully removed {file_path}")
    except Exception as e:
        print(f"Error while trying to remove {file_path}: {e}")

async def download_and_upload_audio_file(user_id: str, file_name: str):
    try:
        # bucket_name = "medvoice_audio_bucket"
        file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{file_name}"
        # Send a GET request to the URL
        response = requests.get(file_url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            file_path = os.path.join("audios", file_url.split("/")[-1])
            # Open the local file in write mode
            with open(file_path, 'wb') as f:
                # Write the contents of the response to the file
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"File downloaded successfully to {file_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

        audio_file = save_audio(file_path, user_id)
        print(audio_file)
        upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], audio_file['new_file_name'], audio_file['new_file_name'])

        remove_file(audio_file["new_file_name"])

        return {
            "new_file_name": audio_file['new_file_name'], 
            "file_id": audio_file['file_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))