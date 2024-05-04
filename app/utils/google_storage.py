from google.cloud import storage
import os

def upload_file_helper(project_id, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # Make the blob publicly accessible.
    blob.make_public()

    print(
        "File {} uploaded to {} and made publicly accessible.".format(
            source_file_name, destination_blob_name
        )
    )

    os.remove(source_file_name)

    print(
        "File {} has been removed from audios/ directory.".format(
            source_file_name
        )
    )