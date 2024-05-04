import replicate
import os
import tempfile
import datetime
import uvicorn
from typing import List
import pvfalcon
import pvleopard

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from google.cloud import storage
from .utils.pretty_print_json import pretty_print_json
from .utils.google_storage import upload_file_helper
from .utils.save_audio import save_audio


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

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
async def upload_file(id: str, file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # The path of the audio file is now 'new_audio_path'
        temp_audio_path, new_filename = save_audio(contents, id)

        project_id="nifty-saga-417905"
        # The name for the new bucket
        bucket_name = "medvoice-sgp-audio-bucket"

        # Call the upload_blob function
        upload_file_helper(project_id, bucket_name, temp_audio_path, new_filename)

        file_url = f"https://storage.googleapis.com/{bucket_name}/{new_filename}"

        output = ''
        # output = replicate.run(
        #     "thomasmol/whisper-diarization:b9fd8313c0d492bf1ce501b3d188f945389327730773ec1deb6ef233df6ea119",
        #     # audio file test: "https://storage.googleapis.com/medvoice-sgp-audio-bucket/what-is-this-what-are-these-63645.mp3"
        #     input={
        #         "file": file_url,
        #         "prompt": "Mark and Lex talking about AI.",
        #         "file_url": "",
        #         "num_speakers": 2,
        #         "group_segments": True,
        #         "offset_seconds": 0,
        #         "transcript_output_format": "segments_only"
        #     }
        # )
        # # output = pretty_print_json(output)
        # output = llama_2(output)

        return {"file_url": file_url, "output": output if output != '' else "It is working"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def llama_2(output):

    result = ''
    # The meta/llama-2-70b-chat model can stream output as it's running.
    for event in replicate.stream(
        "meta/llama-2-70b-chat",
        input={
            "top_k": 0,
            "top_p": 1,
            "prompt": f"""Summarize the transcript organized by key topics.
                If someone has said something important, mention it as: '<Name of the person> made a significant contribution by stating that <important statement>'
                At the bottom, list out the follow up actions if discussed
                ----
                Transcript: {output}
            """,
            "temperature": 0.5,
            "system_prompt": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.",
            "length_penalty": 1,
            "max_new_tokens": 500,
            "min_new_tokens": -1,
        },
    ):
        result += str(event)
    print("\nLlama 2 Result: " + result)
    return result

@app.post("/process_audio")
async def process_audio(file: UploadFile, user_id="1", access_key="XqSUBqySs7hFkIfYiPZtx27L59XDKnzZzAM7rU5pKmjGGFyDf+6bvQ=="):
    try:
        falcon = pvfalcon.create(access_key=access_key)
        leopard = pvleopard.create(access_key=access_key)

        contents = await file.read()
        filename = file.filename

        audio_file = {}
        # The path of the audio file is now 'new_audio_path'
        audio_file = save_audio(contents, filename, user_id)
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

def main():
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()