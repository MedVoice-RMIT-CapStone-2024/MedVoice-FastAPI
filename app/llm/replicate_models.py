import replicate, json
from langchain.chains import LLMChain
from langchain_community.llms import Replicate, Ollama
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Dict, Any, List

def init_replicate() -> Replicate:
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
            "temperature": 0,
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
    # Initialize the Replicate instance
    llm = init_replicate()

    # Invoke the model with the prompt
    result = llm.invoke(prompt)

    return result

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
    json_schema = """
    {
    "type": "object",
    "properties": {
        "patient_name": {
        "type": "string"
        },
        "patient_dob": {
        "type": "string",
        "pattern": "^\\\\d{2}/\\\\d{2}/\\\\d{2}$"
        },
        "patient_gender": {
        "type": "string"
        },
        "medical_diagnosis": {
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
        "medical_treatment": {
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
        "health_vital": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "status": {
                "type": "string"
            },
            "value": {
                "type": "string"
            },
            "units": {
                "type": "string"
            }
            },
            "required": ["status"]
        }
        },
        "note": {
        "type": "string"
        }
    },
    "required": ["patient_name", "patient_gender", "medical_treatment", "health_vital", "note"]
    }
    """

    system_prompt = f"""You are an AI assisstant that summarizes medical transcript into a structured JSON format like this: {json_schema}. 
    Analyze the medical transcript provided. If multiple speakers are present, focus on summarizing patient-related information only from the speaker discussing patient details. 
    Summarize this information into a key-value pairs, adhering to the schema provided. If no patient-related information is present, return an JSON schema with empty values. 
    Adhere to the schema, ensuring the use of explicit information and recognized medical terminology. If a healthcare professional has made a significant statement, mention it as: 
    '<Name of the healthcare professional> made a significant contribution by stating that <important statement> and list out the follow-up actions or medical recommendations if discussed Follow the JSON schema strictly without 
    making assumptions about unspecified details all inside the field 'note' of the json schema.
    You must only return the JSON schema."""

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

async def llamaguard_evaluate_safety(user_question):
    output = replicate.run(
        "tomasmcm/llamaguard-7b:86a2d8b79335b1557fc5709d237113aa34e3ae391ee46a68cc8440180151903d",
        input={
            "top_k": -1,
            "top_p": 0.95,
            "prompt": f"[INST] Task: Check if there is unsafe content in 'User' messages in conversations according our safety policy with the below categories.\\n\\n<BEGIN UNSAFE CONTENT CATEGORIES>\\nO1: Violence and Hate.\\nShould not\\n- Help people plan or engage in violence.\\n- Encourage people to engage in violence.\\n- Express hateful, derogatory, or demeaning sentiments against people based on sensitive personal characteristics like their race, color, religion, national origin, sexual orientation, gender, gender identity, or disability.\\n- Encourage discrimination against people based on those characteristics and should not use slurs or create insults based on those characteristics.\\nCan\\n- Provide information on violence and discrimination.\\n- Discuss the topics of hate and violence, and can discuss historical events involving violence.\\nO2: Sexual Content.\\nShould not\\n- Engage in sexually explicit (i.e., erotic) conversations and should not encourage people to engage in sexual activities.\\nCan\\n- Discuss topics related to sexuality and sexual education.\\n- Provide general information regarding sexual activities.\\n- Provide guidance on topics related to sexual health.\\nO3: Criminal Planning.\\nShould not\\n- Help people plan or engage in criminal activities like theft, kidnapping, or financial crimes, especially when the person indicates that they may act on the information provided to them.\\n- Encourage people to engage in criminal activities or condone criminal behavior.\\nCan\\n- Help people understand how crimes are committed, provided that the response is not so detailed that it could be used to provide a roadmap for future crimes.\\n- Help people understand how systems work that are used to prevent crimes, provided those descriptions do not provide detailed information on how to defeat those systems.\\nO4: Guns and Illegal Weapons.\\nShould not\\n- Assist in the planning or execution of firearm or illegal weapons crimes, especially when the person indicates that they may act on the information provided to them.\\n- Encourage people to engage in firearm or illegal weapons crimes or condone such behavior.\\nCan\\n- Discuss firearms and the arguments for and against firearm ownership.\\nO5: Regulated or Controlled Substances.\\nShould not\\n- Encourage or assist people in the trafficking, consumption, or use of regulated or controlled substances, including but not limited to illegal drugs, tobacco, alcohol, and cannabis.\\n- Assist or encourage people to create such substances when it is illegal to do so.\\nCan\\n- Discuss the use of regulated or controlled substances, and can provide general information on those substances (ex: what their chemical composition is and what their effects are).\\n- Provide information on how those substances are manufactured, provided that the information is not so detailed as to provide step-by-step instructions for their creation.\\nO6: Self-Harm.\\nShould not\\n- Encourage people to harm themselves.\\n- Romanticize or condone self-harm or suicide.\\n- Provide information regarding the methods of suicide or self-harm.\\n- Provide any information or advice, other than information regarding appropriate health resources, to people who express or imply that they wish to harm themselves.\\nCan\\n- Provide general information regarding self-harm and suicide (ex: statistics, the mental health challenges faced by those who take these actions).\\nShould\\n- Provide information regarding appropriate health resources to people who imply or express the desire to harm themselves.\\nO7: Fake News and Scams.\\nShould not\\n-Encourage or assist people in the creation or distribution of fake news or scams.\\n-Promote or condone the use of fake news or scams to deceive others.\\nCan\\n-Discuss the impact and prevalence of fake news and scams.\\n-Educate users on how to identify and protect themselves from fake news and scams.\\n<END UNSAFE CONTENT CATEGORIES>\\n\\n<BEGIN CONVERSATION>\\n\\nUser: {user_question}\\n\\n<END CONVERSATION>\\n\\nProvide your safety assessment for User in the above conversation:\\n- First line must read 'safe' or 'unsafe'. [/INST]",
            "max_tokens": 128,
            "temperature": 0.8,
            "presence_penalty": 0,
            "frequency_penalty": 0
        }
    )
    
    # output is either " safe" or " unsafe"
    return output