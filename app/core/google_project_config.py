from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
cloud_details = {
    "project_id": os.getenv("GCLOUD_PROJECT_ID"),
    "bucket_name": os.getenv("GCLOUD_STORAGE_BUCKET")
}