import re
from google.cloud import storage
from typing import List
from datetime import datetime

from more_itertools import bucket

from ..core.google_project_config import cloud_details

def init_storage_client():
    """Initializes and returns an authenticated storage client and bucket."""
    storage_client = storage.Client(project=cloud_details['project_id'])
    bucket = storage_client.bucket(cloud_details['bucket_name'])
    return bucket

def upload_file_to_bucket(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    bucket = init_storage_client()
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # Make the blob publicly accessible.
    # blob.make_public()

    print(
        "File {} uploaded and made publicly accessible.".format(
            source_file_name
        )
    )

    file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{source_file_name}"

    return file_url

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

    # Extract dates and filter out None values
    date_links = [(link, get_datetime_from_link(link)) for link in links]
    date_links = [(link, date_time) for link, date_time in date_links if date_time is not None]

    # Sort the links based on the date-time
    sorted_links = sorted(date_links, key=lambda x: x[1], reverse=True)

    # Return only the links, sorted
    return [link for link, _ in sorted_links]