import os
import datetime
import hashlib

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

# Helper function
def get_file_info(file_path):
    # Use os.path.splitext to split the file path into root and extension
    file_name, file_extension = os.path.splitext(file_path)
    # Return the file extension
    return {"file_name": file_name, "file_extension": file_extension}