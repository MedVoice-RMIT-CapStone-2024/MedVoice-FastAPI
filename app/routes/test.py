import os, requests, json

from fastapi import HTTPException

from ..utils.file_manipulation import pretty_print_json, remove_file
from ..utils.google_storage import upload_file_to_bucket
from ..utils.save_file import save_audio
from ..models.replicate_models import llama3_generate_medical_json, convert_prompt_for_llama3, whisper_diarization, llamaguard_evaluate_safety
# from ..models.picovoice_models import picovoice_models
from ..config.google_project_config import cloud_details

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

        remove_file(audio_file["new_file_name"])

        return {
            "new_file_name": audio_file['new_file_name'], 
            "file_id": audio_file['file_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def whisper_diarize(file_url: str):
    try:
        output = await whisper_diarization(file_url)
        print(pretty_print_json(output))
        prompt_for_llama3 = convert_prompt_for_llama3(output)
        input_transcript = prompt_for_llama3["input_transcript"]

        return input_transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def llm_pipeline_audio_to_json(file_url: str):
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
        
async def llamaguard_evaluate(question: str):
    try:
        output = await llamaguard_evaluate_safety(question)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
