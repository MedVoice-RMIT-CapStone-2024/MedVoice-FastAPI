from pygments import highlight, lexers, formatters
from fastapi import HTTPException
from typing import List, Dict, Any, Optional, Union
import json, os, requests, datetime, hashlib

from ..core.google_project_config import *
from .bucket_helpers import upload_file_to_bucket

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
    
def save_audio(file_path: str, user_id: str):
    # Ensure the audios/ directory exists
    os.makedirs('audios', exist_ok=True)

    temp_audio_path = file_path

    # Get file extension
    file_info = get_file_info(temp_audio_path)
    file_name, file_extension = file_info['file_name'], file_info['file_extension']

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the new file_name with date, original file_name, and user ID
    new_file_name = f'{file_name}patient_{date_string}date_{user_id}{file_extension}'

    # Hash this new file_name
    file_id = hashlib.sha256(new_file_name.encode('utf-8')).hexdigest()

    # Create the new file_name with hash value, date, original file_name, and user ID
    new_file_name = f'{file_name}patient_{date_string}date_{file_id}fileID_{user_id}{file_extension}'
    
    # Rename the temporary file
    # new_audio_path = os.path.join('audios', new_file_name)
    os.rename(file_path, new_file_name)

    return {"new_file_name": new_file_name, "file_id": file_id}

def save_output(data: Union[List[str], Dict[str, Any]], file_id: str, user_id: str, file_name: Optional[str] = "transcript") -> str:
    # Ensure 'outputs' directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Determine output format based on data type
    if isinstance(data, list):
        output_format = 'txt'
        data_to_write = '\n'.join(data)
    elif isinstance(data, dict):
        output_format = 'json'
        data_to_write = json.dumps(data)
    else:
        raise ValueError("Unsupported data type for saving")

    # Define the full file path
    file_extension = output_format
    output_file_path = os.path.join('outputs', f'{file_id}_{file_name}_{user_id}_output.{file_extension}')

    # Write data to the file
    with open(output_file_path, 'w') as f:
        f.write(data_to_write)

    print(f"Output saved to {output_file_path}")

    return output_file_path

# Helper function for file information
def get_file_info(file_path):
    # Use os.path.splitext to split the file path into root and extension
    file_name, file_extension = os.path.splitext(file_path)
    # Return the file extension
    return {"file_name": file_name, "file_extension": file_extension}

# Helper function for saving JSON to text for picovoice models

# def save_json_to_text(json_output: List[Dict[str, Any]], file_id: str, file_name: Optional[str] = None) -> str:
#     # Ensure 'outputs' directory exists
#     if not os.path.exists('outputs'):
#         os.makedirs('outputs')

#     # Convert each dictionary in 'json_output' to text
#     json_output_text = '\n'.join(json.dumps(item) for item in json_output)

#     # Define the full file path
#     output_file_path = os.path.join('outputs', f'{file_id}_{file_name}_json_output.txt')

#     # Write 'json_output' to a file in the 'outputs' directory
#     with open(output_file_path, 'w') as f:
#         f.write(json_output_text)

#     print(f"'json_output' saved to {output_file_path}")

#     return output_file_path