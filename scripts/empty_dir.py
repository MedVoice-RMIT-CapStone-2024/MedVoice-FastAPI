import os
import shutil

def remove_files_in_directories(directories):
    for directory in directories:
        # Get a list of all files in the directory
        files = os.listdir(directory)

        # Loop through the list of files
        for file_name in files:
            # Skip the placeholder.txt file
            if file_name == 'placeholder.txt':
                continue

            # Create a full file path
            file_path = os.path.join(directory, file_name)
            
            # Check if the path is a file or a directory
            if os.path.isfile(file_path):
                # Remove the file
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # Remove the directory and all its contents
                shutil.rmtree(file_path)

# Usage:
remove_files_in_directories(['audios', 'outputs'])
