import os
import tempfile
import datetime

def save_audio(contents):
    # Ensure the audios/ directory exists
    os.makedirs('audios', exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir='audios') as temp_audio:
        temp_audio.write(contents)
        temp_audio_path = temp_audio.name

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Rename the temporary file to include the date and time
    new_audio_path = os.path.join('audios', f'{date_string}.mp3')
    os.rename(temp_audio_path, new_audio_path)

    # The path of the audio file is now 'new_audio_path'
    temp_audio_path = new_audio_path

    return temp_audio_path
