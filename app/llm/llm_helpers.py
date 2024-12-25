from typing import Dict, List, Optional, Any

from .prompt import (
    SYSTEM_PROMPT_TEMPLATE,
    MEDICAL_OUTPUT_EXAMPLE
)

def extract_transcript_with_speakers(data: List[Dict[str, Any]]) -> str:
    """
    Extracts a structured transcript with speaker mapping from the given data.
    Stops processing if a 'chunks' field is encountered.

    :param data: List of dictionaries containing 'text', 'speaker', and optional 'chunks' fields.
    :return: A formatted transcript string with speaker mapping.
    """
    if not isinstance(data, list):
        raise ValueError("Input data must be a list of dictionaries.")
    
    input_transcript = ""
    speaker_map: Dict[str, str] = {}

    for item in data:
        # Stop processing if 'chunks' field is present
        if "chunks" in item:
            break

        speaker = item.get("speaker", "UNKNOWN")
        
        # Map speakers to speaker numbers if not already mapped
        if speaker not in speaker_map:
            speaker_number = str(len(speaker_map) + 1)
            speaker_map[speaker] = speaker_number
        
        speaker_number = speaker_map[speaker]
        
        # Append the formatted text to the transcript
        input_transcript += f"Speaker {speaker_number}: {item['text']}\n"
        
    print(input_transcript)
    return input_transcript

def convert_prompt_for_llama3(data: List[Dict[str, Any]], patient_name: Optional[str] = None) -> Dict[str, str]:
    """
    Converts the transcript data into a formatted prompt for LLaMA 3.
    
    :param data: List of dictionaries containing transcript data
    :param patient_name: Optional patient name to include in the prompt
    :return: Dictionary containing the prompt and input transcript
    """
    input_transcript = extract_transcript_with_speakers(data)

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
