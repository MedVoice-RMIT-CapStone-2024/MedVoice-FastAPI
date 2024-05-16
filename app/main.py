import os, uvicorn, nest_asyncio, requests

from typing import List, Union, cast, Optional
from google.cloud import storage
from pyngrok import ngrok
from contextlib import asynccontextmanager
from pydantic import BaseModel

from fastapi import FastAPI, Request, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .utils.pretty_print_json import pretty_print_json
from .utils.google_storage import upload_file_helper
from .utils.save_audio import save_audio
from .models.replicate_models import llama_2, whisper_diarization
from .models.picovoice_models import picovoice_models

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

# Mounting local directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/audios", StaticFiles(directory="audios"), name="audios")

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
async def authenticate_implicit_with_adc(project_id="nifty-saga-417905"):
    """
    When interacting with Google Cloud Client libraries, the library can auto-detect the
    credentials to use.

    // TODO(Developer):
    //  1. Before running this sample,
    //  set up ADC as described in https://cloud.google.com/docs/authentication/external/set-up-adc
    //  2. Replace the project variable.
    //  3. Make sure that the user account or service account that you are using
    //  has the required permissions. For this sample, you must have "storage.buckets.list".
    Args:
        project_id: The project id of your Google Cloud project.
    """

    # This snippet demonstrates how to list buckets.
    # *NOTE*: Replace the client created below with the client required for your application.
    # Note that the credentials are not specified when constructing the client.
    # Hence, the client library will look for credentials using ADC.
    storage_client = storage.Client(project=project_id)
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        bucket_name = bucket.name
        print(bucket.name)
    print("Listed all storage buckets.")
    return "Bucket: " + bucket_name

@app.get("/get_audio/{id}")
async def get_audio(id: str):
    try:
        # Your Google Cloud project ID and bucket name
        project_id="nifty-saga-417905"
        # The name for the new bucket
        bucket_name = "medvoice-sgp-audio-bucket"

        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)

        # Get the list of blobs in the bucket
        blobs = bucket.list_blobs()

        # Create a list to store the URLs of the audio files
        audio_urls = []

        # Iterate over the blobs to find the ones that end with the id
        for blob in blobs:
            # Split the blob name by underscore and get the last part before the extension
            id_in_blob = blob.name.rsplit('.', 1)[0].rsplit('_', 1)[-1]
            """
            TODO: Compare the current date with the file date 
            """

            # Check if the id in the blob name matches the id
            if id_in_blob == id:
                # Add the public URL of the blob to the list
                audio_urls.append(blob.public_url)

        # Return the list of audio URLs
        return {"urls": audio_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile, user_id, url: Optional[str] = None):
    try:
        if url:
            file = await download_file(url)
            new_file_name = file('file')
        else:
            contents = await file.read()

            audio_file = {}
            # The path of the audio file is now 'new_audio_path'
            audio_file = save_audio(contents, file.file_name, user_id)
            temp_audio_path, new_file_name = audio_file['temp_audio_path'], audio_file['new_file_name']

        project_id="nifty-saga-417905"
        # The name for the new bucket
        bucket_name = "medvoice-sgp-audio-bucket"

        # Call the upload_blob function
        upload_file_helper(project_id, bucket_name, temp_audio_path, new_file_name)

        file_url = f"https://storage.googleapis.com/{bucket_name}/{new_file_name}"

        output = ''
        # output = pretty_print_json(output)
        output = await llama_2(whisper_diarization(file_url))

        return {"file_url": file_url, "output": output if output != '' else "It is working"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_audio")
async def process_audio(user_id: str, file_name: str, access_key="XqSUBqySs7hFkIfYiPZtx27L59XDKnzZzAM7rU5pKmjGGFyDf+6bvQ=="):
    try:
        audio_file = await download_file(user_id, file_name)
        new_file_name, file_id = audio_file['new_file_name'], audio_file['file_id']

        picovoice_outputs = picovoice_models(new_file_name, access_key)

        sentences_v2 = picovoice_outputs["sentences_v2"]
        """
        TODO: 
        - Save the sentences_v2 JSON file to the same cloud bucket as the file_name
        - From sentences_v2 -> llama-3 to reformat to custom fields -> new JSON/Text file
        - Response new JSON/Text file to FE
        - FE to display the new JSON/Text file under an UI
        """
        
        os.remove(new_file_name)

        """
        TODO:
        - Upload new file name to the cloud bucket
        - Delete the original file name on bucket
        """

        return {
            "sentences": picovoice_outputs["sentences"],
            "sentences_v2": picovoice_outputs["sentences_v2"],
            "file_id": file_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/download")
async def download_file(user_id: str, file_name: str):
    try:
        bucket_name = "medvoice_audio_bucket"
        file_url = f"https://storage.googleapis.com/{bucket_name}/{file_name}"
        # Send a GET request to the URL
        response = requests.get(file_url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            file_path = os.path.join("audios", file_url.split("/")[-1])
            # Open the local file in write mode
            with open(file_path, 'wb') as f:
                # Write the contents of the response to the file
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"File downloaded successfully to {file_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

        audio_file = save_audio(file_path, user_id)
        print(audio_file)

        return {
            "new_file_name": audio_file['new_file_name'], 
            "file_id": audio_file['file_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    # specify a port
    port = 8000
    ngrok_tunnel = ngrok.connect(port)

    # where we can visit our fastAPI app
    print('Public URL:', ngrok_tunnel.public_url)


    nest_asyncio.apply()
    uvicorn.run(app, port=8000, log_level="info")

main()