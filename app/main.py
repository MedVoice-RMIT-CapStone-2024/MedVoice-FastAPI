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
from .utils.json_helpers import *
from .llm.rag import RAGSystem_JSON
from .core.google_project_config import *
from .core.app_config import ON_LOCALHOST, RAG_SYS
from .models.request_models import *
from .worker import *
from .db.init_db import initialize_all_databases


# Determine if running in Docker
running_in_docker = os.getenv('RUNNING_IN_DOCKER', 'false') == 'true'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up...")
    if not ON_LOCALHOST:
        # Only initialize database when not in local development
        print("Initializing databases...")
        await initialize_all_databases()
    else:
        print("Running in local mode - skipping database initialization")
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

# Include API router
from .api.v1.api_v1_router import api_router
app.include_router(api_router)

@app.get("/")
def index(request: Request):
    """Render the index.html template."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/get_transcript/{file_id}/{file_extension}", tags=["process-transcript"])
async def get_transcript(file_id: str, file_extension: FileExtension):
    """
    Retrieve the transcript of a file by its ID and file extension.

    - If the file is JSON, return the parsed JSON.
    - If the file is TXT, return the text as a dictionary.
    """
    try:
        bucket = init_storage_client()
        blobs = bucket.list_blobs()
        for blob in blobs:
            last_part = blob.name.rsplit("/", 1)[-1]
            id_in_blob = last_part.split("_", 1)[0]

            if id_in_blob == file_id and last_part.endswith(f".{file_extension}"):
                response = requests.get(blob.public_url)
                if file_extension == FileExtension.json:
                    return response.json()
                elif file_extension == FileExtension.txt:
                    return {"transcript": response.text}

        return {"message": f"No file found with ID {file_id} and extension .{file_extension}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_json_transcripts_by_user/{user_id}", tags=["process-transcript"])
async def get_transcripts_by_user(user_id: str):
    """
    Retrieve all patient data generated by the LLM for a specific user.
    """
    try:
        bucket = init_storage_client()
        blobs = bucket.list_blobs()
        patients = []

        for blob in blobs:
            split_parts = blob.name.rsplit(".", 1)[0].rsplit("_", 2)
            if len(split_parts) < 3:
                continue

            user_id_in_blob = split_parts[-2]
            if user_id_in_blob == user_id and blob.name.endswith(".json"):
                response = requests.get(blob.public_url)
                json_data = response.json()
                patient_data = remove_json_metadata(json_data)
                patients.append(patient_data)

        return {"patients": patients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process_transcript", tags=["process-transcript"])
async def process_transcript(
    transcript: List[str],
    file_id: Optional[str] = None,
    file_extension: Optional[AudioExtension] = AudioExtension.m4a,
    user_id: Optional[str] = None,
    file_name: Optional[str] = None,
):
    """
    Process and save the transcript of an audio file.

    - Download the specified file.
    - Process the transcript text.
    - Save the result to cloud storage.
    """
    try:
        if user_id and file_name:
            audio_file = await fetch_and_store_audio(user_id, file_name)
            file_id = audio_file["file_id"]
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
            raise ValueError("Transcript must be provided")

        transcript_text = "\n".join(transcript)
        transcript_file_path = generate_output_filename(transcript, file_id, file_name)

        upload_file_to_bucket(transcript_file_path, transcript_file_path)

        remove_local_file(audio_file_path)
        remove_local_file(transcript_file_path)

        return {"transcript": transcript_text, "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process_audio_v2/{user_id}", tags=["process-audio"])
async def process_audio_v2(
    user_id: str,
    file_id: Optional[str] = None,
    file_extension: AudioExtension = AudioExtension.m4a,
    file_name: Optional[str] = None,
):
    """
    Process an audio file and save the output to a cloud storage bucket.

    - Uses Celery for asynchronous processing.
    """
    task = process_audio_task.delay(file_id, file_extension, user_id, file_name)
    return {
        "message": "Audio processing started in the background",
        "task_id": task.id,
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
            "llama3_json_output": result["llama3_json_output"],
        }
    return {"status": task_result.state}


@app.post("/ask_v2/{user_id}", tags=["rag-system"])
async def rag_system_v2(user_id: str, question_body: Question):
    """
    Ask a question to the RAG System.

    - Uses LLM for generating answers.
    - Removes temporary files after processing.
    """
    file_path = f"assets/patients_from_user_{user_id}.json"

    if os.path.exists(file_path):
        remove_local_file(file_path)

    question = question_body.question
    json_data = await get_transcripts_by_user(user_id)

    print(json_data)

    try:
        with open(file_path, "w") as json_file:
            json.dump(json_data, json_file)

        rag_json = RAGSystem_JSON(file_path=file_path)
        answer = await rag_json.handle_question(question)

        remove_local_file(file_path)
        return {"response": answer, "message": "Question answered successfully"}
    except Exception as e:
        if os.path.exists(file_path):
            remove_local_file(file_path)
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point for application setup."""
    load_dotenv()
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    if not ON_LOCALHOST:
        api_key = os.getenv("NGROK_API_KEY")
        pyngrok_config = conf.PyngrokConfig(
            api_key=api_key,
            config_path=os.getenv("NGROK_CONFIG_PATH") if running_in_docker else None,
        )
        conf.set_default(pyngrok_config)
        ngrok_tunnel = ngrok.connect(name=os.getenv("NGROK_TUNNEL", "medvoice_backend"))
        
        print("Public URL:", ngrok_tunnel.public_url)
        nest_asyncio.apply()
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)

main()