import os
import datetime
import hashlib
import json
from typing import List, Dict, Any, Optional, Union

from .file_manipulation import get_file_info

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

def save_json_to_text(json_output: List[Dict[str, Any]], file_id: str, file_name: Optional[str] = None) -> str:
    # Ensure 'outputs' directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Convert each dictionary in 'json_output' to text
    json_output_text = '\n'.join(json.dumps(item) for item in json_output)

    # Define the full file path
    output_file_path = os.path.join('outputs', f'{file_id}_{file_name}_json_output.txt')

    # Write 'json_output' to a file in the 'outputs' directory
    with open(output_file_path, 'w') as f:
        f.write(json_output_text)

    print(f"'json_output' saved to {output_file_path}")

    return output_file_path

def save_output(data: Union[List[str], Dict[str, Any]], file_id: str, file_name: Optional[str] = "transcript") -> str:
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
    output_file_path = os.path.join('outputs', f'{file_id}_{file_name}_output.{file_extension}')

    # Write data to the file
    with open(output_file_path, 'w') as f:
        f.write(data_to_write)

    print(f"Output saved to {output_file_path}")

    return output_file_path

