import replicate, os, uvicorn, nest_asyncio, requests
# Picovoice Models
import pvfalcon, pvleopard

from typing import List, Union, cast
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
from .utils.replicate_models import llama_2, whisper_diarization

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
async def upload_file(url: str, user_id: str, file: UploadFile):
    try:
        if url:
            file = download_file(url)
            new_filename = file('file')
        else:
            contents = await file.read()

            audio_file = {}
            # The path of the audio file is now 'new_audio_path'
            audio_file = save_audio(contents, file.filename, user_id)
            temp_audio_path, new_filename = audio_file['temp_audio_path'], audio_file['new_filename']

        project_id="nifty-saga-417905"
        # The name for the new bucket
        bucket_name = "medvoice-sgp-audio-bucket"

        # Call the upload_blob function
        upload_file_helper(project_id, bucket_name, temp_audio_path, new_filename)

        file_url = f"https://storage.googleapis.com/{bucket_name}/{new_filename}"

        output = ''
        # output = pretty_print_json(output)
        output = await llama_2(whisper_diarization(file_url))

        return {"file_url": file_url, "output": output if output != '' else "It is working"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_audio")
async def process_audio(url: str, file: UploadFile, user_id, access_key="XqSUBqySs7hFkIfYiPZtx27L59XDKnzZzAM7rU5pKmjGGFyDf+6bvQ=="):
    try:
        falcon = pvfalcon.create(access_key=access_key)
        leopard = pvleopard.create(access_key=access_key)

        if url:
            file = download_file(url)
            new_filename = file('file')
        else:
            contents = await file.read()

            audio_file = {}
            # The path of the audio file is now 'new_audio_path'
            audio_file = save_audio(contents, file.filename, user_id)
            temp_audio_path, new_filename = audio_file['temp_audio_path'], audio_file['new_filename']

        project_id="nifty-saga-417905"
        # The name for the new bucket
        bucket_name = "medvoice-sgp-audio-bucket"

        # Call the upload_blob function
        upload_file_helper(project_id, bucket_name, temp_audio_path, new_filename)

        segments = falcon.process_file(temp_audio_path)
        transcript, words = leopard.process_file(temp_audio_path)

        sentences = {}
        sentences_v2 = []

        for segment in segments:
            words_for_segment = [word.word for word in words if segment.start_sec <= word.start_sec <= segment.end_sec]

            sentences_v2.append({
                "speaker_tag": segment.speaker_tag,
                "sentence": " ".join(words_for_segment),
                "start_sec": segment.start_sec,
                "end_sec": segment.end_sec
            })

            if segment.speaker_tag in sentences:
                sentences[segment.speaker_tag] += " " + " ".join(words_for_segment)
            else:
                sentences[segment.speaker_tag] = " ".join(words_for_segment)
        
        os.remove(temp_audio_path)

        return {
            "sentences": sentences,
            "sentences_v2": sentences_v2
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/download")
async def download_file(url: str):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            filename = os.path.join("audios", url.split("/")[-1])
            # Open the local file in write mode
            with open(filename, 'wb') as f:
                # Write the contents of the response to the file
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"File downloaded successfully to {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

        return {"file": filename}
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