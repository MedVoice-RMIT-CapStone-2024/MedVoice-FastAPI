import replicate, json
import os
from langchain.chains import LLMChain
from langchain_community.llms import Replicate, Ollama
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Dict, Any, List, Optional, Union

from .prompt import *

HF_ACCESS_TOKEN = os.getenv("HF_ACCESS_TOKEN", "")

def init_replicate() -> Replicate:
    # Initialize the Replicate instance
    llm = Replicate(
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
        model="meta/meta-llama-3.1-405b-instruct",
        model_kwargs={
            "top_k": 0,
            "top_p": 0.9,
            "max_tokens": 4096,
            "temperature": 0.2,
            "length_penalty": 1,
            "stop_sequences": "<|end_of_text|>,<|eot_id|>",
            "presence_penalty": 1.15,
            "log_performance_metrics": False
        },
    )
    return llm

def init_ollama():
    llm = Ollama(model="llama3", temperature=0)
    return llm

async def llama3_generate_medical_json(prompt: str) -> Dict[str, Any]:
    llm = init_replicate()
    
    # Create a PromptTemplate
    prompt_template = PromptTemplate(
        template="{prompt}",
        input_variables=["prompt"]
    )
    
    # Create a runnable sequence
    chain = prompt_template | llm
    
    # Run the chain
    result = await chain.ainvoke({"prompt": prompt})
    
    try:
        # Clean and parse the result
        result = str(result).strip()
        if result.startswith("```json"):
            result = result.split("```json")[1]
        if result.endswith("```"):
            result = result[:-3]
        
        return json.loads(result.strip())
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw output: {result}")
        return {"error": "Failed to parse JSON", "raw_output": result}

async def whisper_diarization(file_url: str):
    output = replicate.run(
        "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
        input={
            "task": "transcribe",
            "audio": file_url,
            "hf_token": HF_ACCESS_TOKEN,
            "language": "None",
            "timestamp": "word",
            "batch_size": 64,
            "diarise_audio": True
        }
    )
    return output

def convert_prompt_for_llama3(data, patient_name: Optional[str] = None) -> str:
    print("Debug - Input data type:", type(data))
    print("Debug - Input data:", json.dumps(data, indent=2))
    
    input_transcript = ""
    speaker_map: Dict[str, str] = {}

    # Handle string input by attempting to parse it as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            # If it's not JSON, treat it as a single utterance
            return {"prompt": data, "input_transcript": data}

    # Now handle the data structure
    if isinstance(data, dict):
        segments = data.get("segments", [])
    elif isinstance(data, list):
        segments = data
    else:
        return {"prompt": str(data), "input_transcript": str(data)}

    for segment in segments:
        if isinstance(segment, dict):
            speaker = segment.get("speaker", "UNKNOWN")
            text = segment.get("text", "")
            
            if speaker not in speaker_map:
                speaker_map[speaker] = str(len(speaker_map) + 1)
            
            speaker_number = speaker_map[speaker]
            input_transcript += f"Speaker {speaker_number}: {text}\n"

    prompt: str = f"""
    System: {SYSTEM_PROMPT_TEMPLATE.format(
        schema=MEDICAL_OUTPUT_EXAMPLE,
        output_schema=MEDICAL_OUTPUT_EXAMPLE,
        patient_name=patient_name
    )}
    User: 
    {input_transcript}
    Assistant:
    """

    return {"prompt": prompt, "input_transcript": input_transcript}

async def llama3_generate_medical_summary(output: str) -> str:
    llm = init_replicate()
    result = ''
    for event in llm.stream(
        input={
            "top_k": 0,
            "top_p": 0.9,
            "prompt": f"""Work through this problem step by step:
                Q: Summarize the medical transcript organized by key topics.
                If a healthcare professional has made a significant statement, mention it as: '<Name of the healthcare professional> made a significant contribution by stating that <important statement>'
                At the end, list out the follow-up actions or medical recommendations if discussed
                ----
                Medical Transcript: {output}
            """,
            "max_tokens": 2048,
            "min_tokens": 1024,
            "temperature": 0.4,
            "system_prompt": "You are a helpful assistant. Only use the information explicitly mentioned in the transcript, and you must not infer or assume any details that are not directly stated.",
            "length_penalty": 1,
            "stop_sequences": "<|end_of_text|>,<|eot_id|>",
            "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant. Your role is to summarize medical transcripts and provide accurate information based on the explicit content of the transcript. You must not infer or assume any details that are not directly stated.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "presence_penalty": 1.15,
            "log_performance_metrics": False
        },
    ):
        result += str(event)
    print("\nMedical Summary Result: " + result)
    return result