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