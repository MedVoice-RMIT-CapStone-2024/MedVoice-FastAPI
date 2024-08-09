import os, uvicorn, nest_asyncio, requests, re, asyncio, datetime

from typing import List, Optional, Dict, Any
from google.cloud import storage
from pyngrok import ngrok, conf
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Request, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from celery.result import AsyncResult

from .utils.bucket_helpers import *
from .utils.file_helpers import *
from .llm.rag import RAGSystem_JSON, RAGSystem_PDF
from .core.google_project_config import *
from .models.req_body import *
from .worker import *
from .db.init_db import initialize_all_databases

# Change the value for the local development
ON_LOCALHOST = True
RAG_SYS = True
# Determine if running in Docker
running_in_docker = os.getenv('RUNNING_IN_DOCKER', 'false') == 'true'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up...")
    asyncio.run(initialize_all_databases())
    yield
    # Code to run on shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Mounting local directory
app.mount("/static", StaticFiles(directory="/workspace/code/static" if running_in_docker else "static"), name="static")
app.mount("/assets", StaticFiles(directory="/workspace/code/assets" if running_in_docker else "assets"), name="assets")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

templates = Jinja2Templates(directory=".")

# API Router
from .api.v1.api_v1_router import api_router
app.include_router(api_router)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

############################################
### Endpoint for working with transcript ### 

@app.get("/get_transcript/{file_id}/{file_extension}", tags=["process-transcript"])
async def get_transcript(file_id: str, file_extension: FileExtension):
    try:
        storage_client = storage.Client(project=cloud_details['project_id'])
        bucket = storage_client.bucket(cloud_details['bucket_name'])

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Iterate over the blobs to find the one that contains the 'file_id' in its name
        for blob in blobs:
            # Split the blob name by slash and get the last part
            last_part = blob.name.rsplit('/', 1)[-1]

            # Split the last part by underscore and get the first part
            id_in_blob = last_part.split('_', 1)[0]

            # Check if the id in the blob name matches the 'file_id' and the file has the correct extension
            if id_in_blob == file_id and last_part.endswith(f".{file_extension}"):
                # Get the content of the blob
                response = requests.get(blob.public_url)
                if file_extension == FileExtension.json:
                    # Render the blob.public_url to a JSON object and return it
                    return response.json()
                elif file_extension == FileExtension.txt:
                    # Render the blob.public_url to a transcript_text and return it as a object {"transcript": transcript_text}
                    transcript_text = response.text
                    return {"transcript": transcript_text}

        # If no matching blob is found, return a message saying that there is no such file with that ID
        return {"message": f"No file found with ID {file_id} and extension .{file_extension}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_transcript", tags=["process-transcript"])
async def process_transcript(transcript: List[str], file_id: Optional[str] = None, file_extension: Optional[AudioExtension] = AudioExtension.m4a, user_id: Optional[str] = None, file_name: Optional[str] = None):
    try:
        # Transcript list of strings test: ["This", "is", "a", "test", "transcript"]
        # Download the file specified by 'user_id' and 'file_name' asynchronously
        if user_id and file_name:
            audio_file = await encode_audio_filename(user_id, file_name)
            # Extract the new file name and file id from the downloaded file's details
            file_id = audio_file['file_id']
            audio_file_path = None
        elif file_id:
            # Getting the url of the audio file
            file_url = await get_audio(file_id, file_extension)
            # Extract the audio file path from the url
            audio_file_path = get_file_path(file_url)

            # Define a regex pattern to extract the patient from the file name
            pattern = r'(.*?)patient_'
            
            match = re.search(pattern, audio_file_path)
            if match:
                patient = match.group(1)
                file_name = patient.replace('patient_', '')
                print(f"Patient name: {file_name}")

        if not transcript:
            raise ValueError("transcript must be provided")
        
        # Convert the list of strings to a single string
        transcript_text = '\n'.join(transcript)

        transcript_file_path = save_output(transcript, file_id, file_name)

        # Upload the output file to a cloud storage bucket
        transcript_url = upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)

        rm_local_file(audio_file_path)
        rm_local_file(transcript_file_path)

        return {"transcript": transcript_text, "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
### Endpoint for working with transcript ### 
############################################

#####################################################
### Endpoint for process audio with LLM pipeline ###

@app.post("/process_audio_v2", tags=["process-audio"])
async def process_audio_v2(file_id: Optional[str] = None, file_extension: AudioExtension = AudioExtension.m4a, user_id: Optional[str] = None, file_name: Optional[str] = None):
    # Dispatch the Celery task
    task = process_audio_task.delay(file_id, file_extension, user_id, file_name)
    
    # Return a response indicating the task was successfully dispatched
    return {
        "message": "Audio processing started in the background", 
        "task_id": task.id
    }

@app.get("/get_audio_task/{task_id}", tags=["process-audio"])
async def get_audio_processing_result(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.ready():
        result = task_result.get()
        if "error" in result:
            return {"status": task_result.state, "error": result["error"]}
        return {
            "status": task_result.state,
            "file_id": result["file_id"],
            "llama3_json_output": result["llama3_json_output"]
        }
    else:
        return {"status": task_result.state}

### End of endpoint for process audio with LLM pipeline ###
###########################################################

@app.post("/ask", tags=["rag-system"])
async def rag_system(question_body: Question):
    question = question_body.question
    source_type = question_body.source_type
    try: 
        if RAG_SYS:
            # Assuming RAGSystem_PDF and RAGSystem_JSON are defined elsewhere
            rag_pdf = RAGSystem_PDF("assets/update-28-covid-19-what-we-know.pdf")
            rag_json = RAGSystem_JSON("assets/patients.json")
        
            if source_type == SourceType.pdf:
                answer = await rag_pdf.handle_question(question)
            elif source_type == SourceType.json:
                answer = await rag_json.handle_question(question)
        else:
            if source_type == SourceType.pdf:
                answer = f"This is a pdf answer. It is answering to your question: {question}"
            elif source_type == SourceType.json:
                answer = f"This is a json answer. It is answering to your question: {question}"

        task = llamaguard_task.delay(answer)
            
        return {
            "response": answer,
            "message": "Safety processing started in the background", 
            "task_id": task.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def main():
    load_dotenv()

    # Get the API token from environment variable
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
      
    # Create a PyngrokConfig object with the API key and config path
    api_key = os.getenv('NGROK_API_KEY')
    pyngrok_config = conf.PyngrokConfig(
        api_key=api_key, 
        config_path=os.getenv('NGROK_CONFIG_PATH') if running_in_docker else None
    )
    conf.set_default(pyngrok_config)

main()

if ON_LOCALHOST:
    if __name__ == '__main__':
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
else:
    # Open a ngrok tunnel
    ngrok_tunnel = ngrok.connect(name="medvoice_backend")

    # where we can visit our fastAPI app
    print('Public URL:', ngrok_tunnel.public_url)

    # Apply nest_asyncio
    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")