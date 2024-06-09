from pygments import highlight, lexers, formatters
import json, os
from ..config.google_project_config import cloud_details

def pretty_print_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, 
        lexers.JsonLexer(), 
        formatters.TerminalFormatter()
    )
    # print(colorful_json)
    return colorful_json

# Helper function for file information
def get_file_info(file_path):
    # Use os.path.splitext to split the file path into root and extension
    file_name, file_extension = os.path.splitext(file_path)
    # Return the file extension
    return {"file_name": file_name, "file_extension": file_extension}

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