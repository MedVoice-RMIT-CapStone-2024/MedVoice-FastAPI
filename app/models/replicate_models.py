import replicate, json
from langchain.chains import LLMChain
from langchain_community.llms import Replicate
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Dict, Any, List

def initialize_llm() -> Replicate:
    # Initialize the Replicate instance
    llm = Replicate(
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
        model="meta/meta-llama-3-70b-instruct",
        model_kwargs= {
            "top_k": 0,
            "top_p": 0.9,
            "max_tokens": 512,
            "min_tokens": 0,
            "temperature": 0.6,
            "length_penalty": 1,
            "stop_sequences": "<|end_of_text|>,<|eot_id|>",
            "presence_penalty": 1.15,
            "log_performance_metrics": False
        },
    )
    return llm

async def llama3_generate_medical_json(prompt: str) -> Dict[str, Any]:
    # Initialize the Replicate instance
    llm = initialize_llm()

    # Invoke the model with the prompt
    result = llm.invoke(prompt)

    return result

async def llama3_generate_medical_summary(output: str) -> str:
    llm = initialize_llm()
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
            "max_tokens": 512,
            "min_tokens": 0,
            "temperature": 0.6,
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

def convert_prompt_for_llama3(json_output: Dict[str, Any]) -> str:
    # Initialize an empty string for the input transcript
    input_transcript: str = ""

    # Create a dictionary to map speaker IDs to speaker numbers
    speaker_map: Dict[str, str] = {}

    # Iterate over the segments in the JSON output
    for segment in json_output["segments"]:
        # If the speaker ID is not in the map, add it
        if segment["speaker"] not in speaker_map:
            # The speaker number is the next number after the current highest number in the map
            speaker_number: str = str(len(speaker_map) + 1)
            speaker_map[segment["speaker"]] = speaker_number

        # Get the speaker number from the map
        speaker_number = speaker_map[segment["speaker"]]

        # Add the speaker number and text to the input transcript
        input_transcript += f"Speaker {speaker_number}: {segment['text']}\n"

    # Get the prompt from the command line argument
    json_schema="""{
    "type": "object",
    "properties": {
        "name": {
        "type": "string"
        },
        "age": {
        "type": "integer"
        },
        "gender": {
        "type": "string"
        },
        "diagnosis": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "name": {
                "type": "string"
            }
            },
            "required": ["name"]
        }
        },
        "treatment": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "name": {
                "type": "string"
            },
            "prescription": {
                "type": "string"
            }
            },
            "required": ["name", "prescription"]
        }
        },
        "vital": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "name": {
                "type": "string"
            },
            "value": {
                "type": "string"
            },
            "units": {
                "type": "string"
            }
            },
            "required": ["name", "value", "units"]
        }
        }
    },
    "required": ["name", "gender", "treatment", "vital"]
    }"""

    # Define the system prompt
    system_prompt = f"""You are an AI that summarizes medical conversations into a structured JSON format like this{json_schema}. 
    Given the medical transcript below, provide a summary by extracting key-value pairs. Only use the information explicitly mentioned 
    in the transcript, and you must not infer or assume any details that are not directly stated, and strictly follow what the json schema required, 
    and print the json schema only."""

    # Format the prompt for the llama-3 model
    prompt: str = f"""
    System: {system_prompt}
    User: 
    {input_transcript}
    Assistant:
    """

    return {"prompt": prompt, "input_transcript": input_transcript}

async def whisper_diarization(file_url: str): 
    output = replicate.run(
        "thomasmol/whisper-diarization:b9fd8313c0d492bf1ce501b3d188f945389327730773ec1deb6ef233df6ea119",
        # audio file test: "https://storage.googleapis.com/medvoice-sgp-audio-bucket/what-is-this-what-are-these-63645.mp3"
        input={
            "file": file_url,
            "prompt": "Mark and Lex talking about AI.",
            "file_url": "",
            "num_speakers": 2,
            "group_segments": True,
            "offset_seconds": 0,
            "transcript_output_format": "segments_only"
        }
    )

    return output