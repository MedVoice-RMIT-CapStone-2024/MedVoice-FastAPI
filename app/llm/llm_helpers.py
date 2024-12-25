from typing import Dict, List, Optional, Any

from .prompt import (
    SYSTEM_PROMPT_TEMPLATE,
    MEDICAL_OUTPUT_EXAMPLE
)

def extract_transcript_with_speakers(data: List[Dict[str, Any]]) -> str:
    if not isinstance(data, list):
        raise ValueError("Input data must be a list of dictionaries.")
    
    """
    Extracts a concise transcript with speaker mapping from the given data.
    Combines consecutive statements by the same speaker into one line.
    Stops processing if a 'chunks' field is encountered.

    :param data: List of dictionaries containing 'text', 'speaker', and optional 'chunks' fields.
    :return: A formatted, concise transcript string with speaker mapping.
    """
    input_transcript = ""
    speaker_map: Dict[str, str] = {}
    current_speaker = None
    current_text = ""

    for item in data:
        # Stop processing if 'chunks' field is present
        if "chunks" in item:
            break

        speaker = item.get("speaker", "UNKNOWN")
        text = item["text"]
        
        # Map speakers to speaker numbers if not already mapped
        if speaker not in speaker_map:
            speaker_number = str(len(speaker_map) + 1)
            speaker_map[speaker] = speaker_number
        
        speaker_number = speaker_map[speaker]
        
        # Concatenate text if the speaker remains the same
        if speaker == current_speaker:
            current_text += f" {text}"
        else:
            # Add the previous speaker's text to the transcript
            if current_speaker is not None:
                input_transcript += f"Speaker {speaker_map[current_speaker]}: {current_text.strip()}\n"
            # Update to the new speaker
            current_speaker = speaker
            current_text = text

    # Add the last speaker's text
    if current_text:
        input_transcript += f"Speaker {speaker_map[current_speaker]}: {current_text.strip()}\n"

    return input_transcript

def convert_prompt_for_llama3(data: List[Dict[str, Any]], patient_name: Optional[str] = None) -> Dict[str, str]:
    """
    Converts the transcript data into a formatted prompt for LLaMA 3.
    
    :param data: List of dictionaries containing transcript data
    :param patient_name: Optional patient name to include in the prompt
    :return: Dictionary containing the prompt and input transcript
    """
    input_transcript = extract_transcript_with_speakers(data)
    print(f"Input transcript: {input_transcript}")

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
