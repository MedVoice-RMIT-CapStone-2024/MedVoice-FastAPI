from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

# Replace these with your bucket name, source file name, blob name, and destination file name
bucket_name = "your-bucket-name"
source_file_name = "local/path/to/your/file"
destination_blob_name = "storage-object-name"
destination_file_name = "local/path/to/downloaded/file"

# Upload a file to the bucket
upload_blob(bucket_name, source_file_name, destination_blob_name)

# Download a blob from the bucket
download_blob(bucket_name, destination_blob_name, destination_file_name)
