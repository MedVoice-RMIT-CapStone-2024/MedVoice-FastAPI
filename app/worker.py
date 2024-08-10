from celery import Celery

import os, re, asyncio

from typing import Optional

from fastapi import HTTPException

from .utils.bucket_helpers import *
from .utils.file_helpers import *
from .core.google_project_config import *
from .models.req_body import *
from .worker import *
from .llm.replicate_models import llamaguard_evaluate_safety

# API Router
from .api.v1.endpoints.post.llm import *
from .api.v1.endpoints.get.gcloud_storage import *

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(__name__, broker=redis_url, backend=redis_url)

# from .main import process_audio_task
# Autodiscover tasks in the 'app' package, specifically looking in 'main.py'
celery_app.autodiscover_tasks()

async def process_audio_background(file_id: Optional[str] = None, file_extension: Optional[AudioExtension] = AudioExtension.m4a, user_id: Optional[str] = None, file_name: Optional[str] = None):
    try:
        if file_id:
            # Get the url of the audio file
            file_url = await get_audio(file_id, file_extension)
            # Extract the audio file path from the url
            audio_file_path = get_file_path(file_url)

            # Define a regex pattern to extract the patient from the file name
            pattern = r'/(.*?)patient_'
            
            match = re.search(pattern, audio_file_path)
            if match:
                patient = match.group(1)
                file_name = patient.replace('patient_', '')
                print(f"Patient name: {file_name}")

        if user_id and file_name:
            # Download the file specified by 'user_id' and 'file_name' asynchronously
            audio_file = await encode_audio_filename(user_id, file_name)
            # Extract the new file name and file id from the downloaded file's details
            file_id, audio_file_path = audio_file['file_id'], audio_file['new_file_name']
            # Get the url of the audio file
            file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{audio_file_path}"
        
        # Run the LLM pipeline on the audio file url
        llama3_json_output = await llm_pipeline_audio_to_json(file_url)
        print(llama3_json_output)

        transcript_file_path = save_output(llama3_json_output, file_id, file_name)

        # Upload the output file to a cloud storage bucket
        transcript_url = upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)

        rm_local_file(audio_file_path)
        rm_local_file(transcript_file_path)

        return {"file_id": file_id, "llama3_json_output": llama3_json_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@celery_app.task(name="process_audio_task")
def process_audio_task(file_id: Optional[str] = None, file_extension: str = "m4a", user_id: Optional[str] = None, file_name: Optional[str] = None):
    try:
        # Convert the file_extension string back to the AudioExtension enum
        # file_extension = AudioExtension[file_extension.upper()]

        # Run the async function in an event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(process_audio_background(file_id, file_extension, user_id, file_name))
        return result
    except Exception as e:
        # Handle exceptions or log errors
        print(f"Error processing audio: {str(e)}")
        return {"error": str(e)}
    
@celery_app.task(name="llamaguard_task")
def llamaguard_task(question: str):
    try:
        # Run the async function in an event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(llamaguard_evaluate_safety(question))
        return result
    except Exception as e:
        # Handle exceptions or log errors
        print(f"Error processing question: {str(e)}")
        return {"error": str(e)}