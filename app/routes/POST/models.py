import json

from fastapi import HTTPException
from ...utils.file_manipulation import pretty_print_json
from ...models.replicate_models import llama3_generate_medical_json, convert_prompt_for_llama3, whisper_diarization, llamaguard_evaluate_safety
from ...models.rag import RAGSystem_PDF, RAGSystem_JSON

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



    
