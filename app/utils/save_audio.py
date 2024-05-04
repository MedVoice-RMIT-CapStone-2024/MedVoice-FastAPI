import os
import tempfile
import datetime

def save_audio(contents, filename: str, user_id: str):
    # Ensure the audios/ directory exists
    os.makedirs('audios', exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir='audios') as temp_audio:
        temp_audio.write(contents)
        temp_audio_path = temp_audio.name

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the new filename with date, original filename, and user ID
    new_filename = f'{date_string}_{filename}_{user_id}.mp3'

    # Rename the temporary file
    new_audio_path = os.path.join('audios', new_filename)
    os.rename(temp_audio_path, new_audio_path)

    # The path of the audio file is now 'new_audio_path'
    temp_audio_path = new_audio_path

    return {"temp_audio_path": temp_audio_path, "new_filename": new_filename}
