from google.cloud import storage
from typing import List
import re
from datetime import datetime

def upload_file_helper(project_id, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # Make the blob publicly accessible.
    # blob.make_public()

    print(
        "File {} uploaded and made publicly accessible.".format(
            source_file_name
        )
    )

def sort_links_by_datetime(links: List[str]) -> List[str]:
    # Regular expression to match the date-time in the link
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})date")

    # Function to extract the date-time from a link and convert it to a datetime object
    def get_datetime_from_link(link):
        match = pattern.search(link)
        if match:
            date_time_str = match.group(1)
            date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")
            return date_time_obj
        else:
            return None

    # Sort the links based on the date-time
    sorted_links = sorted(links, key=get_datetime_from_link)

    return sorted_links