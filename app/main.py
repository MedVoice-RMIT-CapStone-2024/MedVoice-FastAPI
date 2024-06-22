import os, uvicorn, nest_asyncio, requests, json, re, asyncio

from typing import List, Optional, Dict, Any
from google.cloud import storage
from pyngrok import ngrok, conf
from contextlib import asynccontextmanager
from pydantic import BaseModel
from dotenv import load_dotenv
from enum import Enum

from fastapi import FastAPI, Request, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .utils.file_manipulation import extract_audio_path, remove_file, download_and_upload_audio_file
from .utils.google_storage import upload_file_to_bucket, sort_links_by_datetime
from .utils.save_file import save_output
from .models.rag import RAGSystem_JSON, RAGSystem_PDF
from .config.google_project_config import cloud_details
from .routes.POST.models import llm_pipeline_audio_to_json, whisper_diarize, llamaguard_evaluate_safety

# Change the value for the local development
ON_LOCALHOST = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up...")
    yield
    # Code to run on shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

class File(BaseModel):
    url: str

# Determine if running in Docker
running_in_docker = os.getenv('RUNNING_IN_DOCKER', 'false') == 'true'

# Mounting local directory
app.mount("/static", StaticFiles(directory="/workspace/code/static" if running_in_docker else "static"), name="static")
app.mount("/assets", StaticFiles(directory="/workspace/code/assets" if running_in_docker else "assets"), name="assets")
app.mount("/audios", StaticFiles(directory="/workspace/code/audios" if running_in_docker else "audios"), name="audios")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

templates = Jinja2Templates(directory=".")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/buckets")
async def authenticate_implicit_with_adc():
    # This snippet demonstrates how to list buckets.
    # *NOTE*: Replace the client created below with the client required for your application.
    # Note that the credentials are not specified when constructing the client.
    # Hence, the client library will look for credentials using ADC.
    storage_client = storage.Client(project=cloud_details["project_id"])
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        bucket_name = bucket.name
        print(bucket.name)
    print("Listed all storage buckets.")
    return "Bucket: " + bucket_name

@app.get("/get_audios_from_user/{id}")
async def get_audios_from_user_id(id: str):
    try:
        storage_client = storage.Client(project=cloud_details['project_id'])
        bucket = storage_client.bucket(cloud_details['bucket_name'])

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Create a list to store the URLs of the audio files
        audio_urls = []

        # Iterate over the blobs to find the ones that end with the id
        for blob in blobs:
            # Split the blob name by underscore and get the last part before the extension
            id_in_blob = blob.name.rsplit('.', 1)[0].rsplit('_', 1)[-1]

            # Check if the id in the blob name matches the id
            if id_in_blob == id:
                # Add the public URL of the blob to the list
                audio_urls.append(blob.public_url)

        # Return the list of audio URLs
        return {"urls": sort_links_by_datetime(audio_urls)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FileExtension(str, Enum):
    txt = "txt"
    json = "json"

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "Invalid file extension. Only 'txt' and 'json' are allowed."},
    )

@app.get("/get_transcript/{file_id}/{file_extension}")
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

class AudioExtension(str, Enum):
    mp3 = "mp3"
    wav = "wav"
    m4a = "m4a"

@app.get("/get_audio/{file_id}/{file_extension}")
async def get_audio(file_id: str, file_extension: AudioExtension):
    try:
        storage_client = storage.Client(project=cloud_details['project_id'])
        bucket = storage_client.bucket(cloud_details['bucket_name'])

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Define a regex pattern to extract the fileID from the blob name
        pattern = r'date_(.*?)fileID_'

        # Iterate over the blobs to find the one that matches the 'file_id' and has the correct audio extension
        for blob in blobs:
            # Use regex to extract the fileID from the blob name
            match = re.search(pattern, blob.name)
            if match:
                id_in_blob = match.group(1)
                # Check if the extracted fileID matches the 'file_id' and the file has the correct audio extension
                if id_in_blob == file_id and blob.name.endswith(f".{file_extension}"):
                    # Return the public URL of the blob
                    return blob.public_url

        # If no matching audio file is found, raise an HTTPException
        raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_transcript")
async def process_transcript(transcript: List[str], file_id: Optional[str] = None, file_extension: Optional[AudioExtension] = AudioExtension.m4a, user_id: Optional[str] = None, file_name: Optional[str] = None):
    try:
        # Transcript list of strings test: ["This", "is", "a", "test", "transcript"]
        # Download the file specified by 'user_id' and 'file_name' asynchronously
        if user_id and file_name:
            audio_file = await download_and_upload_audio_file(user_id, file_name)
            # Extract the new file name and file id from the downloaded file's details
            file_id = audio_file['file_id']
            audio_file_path = None
        elif file_id:
            # Getting the url of the audio file
            file_url = await get_audio(file_id, file_extension)
            # Extract the audio file path from the url
            audio_file_path = extract_audio_path(file_url)

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

        remove_file(audio_file_path)
        remove_file(transcript_file_path)

        return {"transcript": transcript_text, "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_audio_v2")
async def process_audio_v2(file_id: Optional[str] = None, file_extension: Optional[AudioExtension] = AudioExtension.m4a, user_id: Optional[str] = None, file_name: Optional[str] = None):
    try:
        if file_id:
            # Get the url of the audio file
            file_url = await get_audio(file_id, file_extension)
            # Extract the audio file path from the url
            audio_file_path = extract_audio_path(file_url)

            # Define a regex pattern to extract the patient from the file name
            pattern = r'/(.*?)patient_'
            
            match = re.search(pattern, audio_file_path)
            if match:
                patient = match.group(1)
                file_name = patient.replace('patient_', '')
                print(f"Patient name: {file_name}")

        if user_id and file_name:
            # Download the file specified by 'user_id' and 'file_name' asynchronously
            audio_file = await download_and_upload_audio_file(user_id, file_name)
            # Extract the new file name and file id from the downloaded file's details
            file_id, audio_file_path = audio_file['file_id'], audio_file['audio_file_path']
            # Get the url of the audio file
            file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{audio_file_path}"
        
        # Run the LLM pipeline on the audio file url
        llama3_json_output = await llm_pipeline_audio_to_json(file_url)
        print(llama3_json_output)

        transcript_file_path = save_output(llama3_json_output, file_id, file_name)

        # Upload the output file to a cloud storage bucket
        transcript_url = upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)

        remove_file(audio_file_path)
        remove_file(transcript_file_path)

        return {"file_id": file_id, "llama3_json_output": llama3_json_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class SourceType(str, Enum):
    pdf = "pdf"
    json = "json"

class Question(BaseModel):
    question: str
    source_type: SourceType

app = FastAPI()

# Assuming RAGSystem_PDF and RAGSystem_JSON are defined elsewhere
rag_pdf = RAGSystem_PDF("update-28-covid-19-what-we-know.pdf")
rag_json = RAGSystem_JSON("prize.json")

@app.post("/ask")
async def rag_system(question_body: Question):
    question = question_body.question
    source_type = question_body.source_type
    try:
        if source_type == SourceType.pdf:
            answer = await rag_pdf.handle_question_async(question)
        elif source_type == SourceType.json:
            answer = await rag_json.handle_question_async(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/test/download")
async def download_route(user_id: str, file_name: str):
    return await download_and_upload_audio_file(user_id, file_name)

@app.post("/test/whisper")
async def whisper_route(file_url: str):
    return await whisper_diarize(file_url)

@app.post("/test/llm")
async def llm_route(file_url: str):
    return await llm_pipeline_audio_to_json(file_url)

@app.post("/test/llamaguard")
async def llamaguard_route(question: str):
    return await llamaguard_evaluate_safety(question)

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

    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")