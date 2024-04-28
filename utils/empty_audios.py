import os
import shutil

# Get a list of all files in the 'audios' directory
audio_files = os.listdir('audios')

# Loop through the list of files
for file_name in audio_files:
    # Create a full file path
    file_path = os.path.join('audios', file_name)
    
    # Check if the path is a file or a directory
    if os.path.isfile(file_path):
        # Remove the file
        os.remove(file_path)
    elif os.path.isdir(file_path):
        # Remove the directory and all its contents
        shutil.rmtree(file_path)