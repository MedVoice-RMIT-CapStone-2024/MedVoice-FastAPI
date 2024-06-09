from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
cloud_details = {
    "project_id": os.getenv("PROJECT_ID"),
    "bucket_name": os.getenv("BUCKET_NAME")
}