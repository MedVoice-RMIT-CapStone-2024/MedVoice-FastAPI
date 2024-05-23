import os, uvicorn, nest_asyncio, requests, json

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

from .utils.pretty_print_json import pretty_print_json
from .utils.google_storage import upload_file_to_bucket, sort_links_by_datetime
from .utils.save_file import save_audio, save_json_to_text, save_strings_to_text, save_json_output
from .models.replicate_models import llama3_generate_medical_summary, llama3_generate_medical_json, convert_prompt_for_llama3, whisper_diarization
from .models.picovoice_models import picovoice_models
from .config.google_project_config import cloud_details

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
async def authenticate_implicit_with_adc():
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
    storage_client = storage.Client(project=cloud_details["project_id"])
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        bucket_name = bucket.name
        print(bucket.name)
    print("Listed all storage buckets.")
    return "Bucket: " + bucket_name

@app.get("/get_audio/{id}")
async def get_audio_by_user_id(id: str):
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
    
@app.post("/process_transcript")
async def process_transcript(user_id: str, file_name: str, transcript: List[str]):
    try:
        # Transcript list of strings test: ["This", "is", "a", "test", "transcript"]
        # Download the file specified by 'user_id' and 'file_name' asynchronously
        audio_file = await download_and_upload_audio_file(user_id, file_name)

        # Extract the new file name and file id from the downloaded file's details
        file_id = audio_file['file_id']

        # Convert the list of strings to a single string
        transcript_text = '\n'.join(transcript)

        transcript_file_path = save_strings_to_text(transcript, file_id, file_name)

        # Upload the output file to a cloud storage bucket
        transcript_url = upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)

        os.remove(transcript_file_path)

        return {"transcript": transcript_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process_audio_v2")
async def process_audio_v2(user_id: str, file_name: str):
    try:
        # Download the file specified by 'user_id' and 'file_name' asynchronously
        audio_file = await download_and_upload_audio_file(user_id, file_name)

        # Extract the new file name and file id from the downloaded file's details
        audio_file_path, file_id = audio_file['new_file_name'], audio_file['file_id']

        file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{audio_file_path}"

        llama3_json_output = await llama_3_70b_instruct_pipeline(file_url)
        print(llama3_json_output)

        transcript_file_path = save_json_output(llama3_json_output, file_id, file_name)

        # Upload the output file to a cloud storage bucket
        transcript_url = upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)

        os.remove(audio_file_path)
        os.remove(transcript_file_path)

        return llama3_json_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_audio")
async def process_audio(user_id: str, file_name: str, access_key="XqSUBqySs7hFkIfYiPZtx27L59XDKnzZzAM7rU5pKmjGGFyDf+6bvQ=="):
    try:
        # Download the file specified by 'user_id' and 'file_name' asynchronously
        audio_file = await download_and_upload_audio_file(user_id, file_name)

        # Extract the new file name and file id from the downloaded file's details
        audio_file_path, file_id = audio_file['new_file_name'], audio_file['file_id']

        # Use the Picovoice models to process the audio file and generate outputs
        picovoice_outputs = picovoice_models(audio_file_path, access_key)

        # Save the 'sentences_v2' output from Picovoice to a file, and get the path of the saved file
        transcript_file_path = save_json_to_text(picovoice_outputs["sentences_v2"], file_id)

        # Upload the output file to a cloud storage bucket
        upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)
        
        # Remove the audio file and output file from the local directory
        os.remove(audio_file_path)
        os.remove(transcript_file_path)

        return {
            "sentences": picovoice_outputs["sentences"],
            "sentences_v2": picovoice_outputs["sentences_v2"],
            "file_id": file_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/test/download")
async def download_and_upload_audio_file(user_id: str, file_name: str):
    try:
        # bucket_name = "medvoice_audio_bucket"
        file_url = f"https://storage.googleapis.com/{cloud_details['bucket_name']}/{file_name}"
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
        upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], audio_file['new_file_name'], audio_file['new_file_name'])

        return {
            "new_file_name": audio_file['new_file_name'], 
            "file_id": audio_file['file_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/whisper")
async def test_whisper_diarization(file_url: str):
    try:
        output = await whisper_diarization(file_url)
        print(pretty_print_json(output))
        prompt_for_llama3 = convert_prompt_for_llama3(output)
        input_transcript = prompt_for_llama3["input_transcript"]

        return input_transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/test/llama3")
async def llama_3_70b_instruct_pipeline(file_url: str):
    num_wrong_output = 0
    while True:
        try:
            speaker_diarization_json = await whisper_diarization(file_url)
            print(pretty_print_json(speaker_diarization_json))
            prompt_for_llama3 = convert_prompt_for_llama3(speaker_diarization_json)
            output = await llama3_generate_medical_json(prompt_for_llama3["prompt"])
            llama3_json_output = json.loads(output)

            # Check if the output is a JSON object
            if isinstance(llama3_json_output, dict):
                try:
                    json.dumps(llama3_json_output)
                    return llama3_json_output
                except (TypeError, OverflowError):
                    num_wrong_output += 1
                    print(f"Error: Output is not a JSON object. Attempt {num_wrong_output}")
                    continue
            else:
                num_wrong_output += 1
                print(f"Error: Output is not a JSON object. Attempt {num_wrong_output}")
                continue

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

def main():
    # specify a port
    # port = 8000
    load_dotenv()

    # Get the API token from environment variable
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    # Get the API key from the environment variable
    api_key = os.getenv('NGROK_API_KEY')
    # Create a PyngrokConfig object with the API key
    pyngrok_config = conf.PyngrokConfig(api_key=api_key)
    conf.set_default(pyngrok_config)
    # Open a ngrok tunnel
    ngrok_tunnel = ngrok.connect(name="medvoice_backend")

    # where we can visit our fastAPI app
    print('Public URL:', ngrok_tunnel.public_url)
    nest_asyncio.apply()
    uvicorn.run(app, port=8000, log_level="info")

main()