import replicate
from pygments import highlight, lexers, formatters
import os
import json
import tempfile
import datetime
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from google.cloud import storage

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
        print(bucket.name)
    print("Listed all storage buckets.")
    return "Buckets are listed in the terminal"

def upload_file_helper(project_id, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # Make the blob publicly accessible.
    blob.make_public()

    print(
        "File {} uploaded to {} and made publicly accessible.".format(
            source_file_name, destination_blob_name
        )
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), project_id="nifty-saga-417905"):
    contents = await file.read()
    # You can now use the contents of the file

    # Ensure the audios/ directory exists
    os.makedirs('audios', exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir='audios') as temp_audio:
        temp_audio.write(contents)
        temp_audio_path = temp_audio.name
        
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Rename the temporary file to include the date and time
    new_audio_path = os.path.join('audios', f'{date_string}.mp3')
    os.rename(temp_audio_path, new_audio_path)

    # The path of the audio file is now 'new_audio_path'
    temp_audio_path = new_audio_path

    # The name for the new bucket
    bucket_name = "medvoice-sgp-audio-bucket"

    # Call the upload_blob function
    upload_file_helper(project_id, bucket_name, temp_audio_path, f'{date_string}.mp3')

    file_url = f"https://storage.googleapis.com/{bucket_name}/{date_string}.mp3"

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

def pretty_print_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, 
        lexers.JsonLexer(), 
        formatters.TerminalFormatter()
    )
    # print(colorful_json)
    return colorful_json

def main():
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()