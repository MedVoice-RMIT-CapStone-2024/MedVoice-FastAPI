import json, requests

from fastapi import HTTPException, Response, APIRouter
from .....utils.file_helpers import pretty_print_json
from .....llm.replicate_models import llama3_generate_medical_json, convert_prompt_for_llama3, whisper_diarization, llamaguard_evaluate_safety
from .....models.req_body import Question

router = APIRouter()

@router.post("/whisper-diarize/")
async def whisper_diarize_endpoint(file_url: str):
    return await whisper_diarize(file_url)

@router.post("/llm-pipeline/")
async def llm_pipeline_audio_to_json_endpoint(file_url: str):
    return await llm_pipeline_audio_to_json(file_url)

@router.post("/llamaguard-evaluate/")
async def llamaguard_evaluate_endpoint(question: str):
    return await llamaguard_evaluate(question)

@router.post("/ask-llama2/")
async def ask_llama2_endpoint(question_body: Question):
    return await ask_llam2(question_body.question)

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
    speaker_diarization_json = await whisper_diarization(file_url)
    prompt_for_llama3 = convert_prompt_for_llama3(speaker_diarization_json)
    while True:
        try:
            print(pretty_print_json(speaker_diarization_json))
            output = await llama3_generate_medical_json(prompt_for_llama3["prompt"])

            raw_output = fr"""{output}"""
            
            # Attempt to parse the output as JSON
            try:
                llama3_json_output = json.loads(raw_output)
            except json.JSONDecodeError as e:
                num_wrong_output += 1
                print(f"Error: Failed to decode JSON. Attempt {num_wrong_output}. Details: {str(e)}")
                continue

            # Check if the parsed output is a dictionary (JSON object)
            if isinstance(llama3_json_output, dict):
                return llama3_json_output
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

async def ask_llam2(question: str):
    res = requests.post("http://ollama:11434/api/generate", 
                        json={
                            "prompt": question,
                            "stream": False,
                            "model": "llama2",
                        })
    return Response(content=res.text, media_type="application/json")


    
