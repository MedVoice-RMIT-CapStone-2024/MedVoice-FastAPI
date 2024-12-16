import replicate, json
from langchain.chains import LLMChain
from langchain_community.llms import Replicate, Ollama
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Dict, Any, List, Optional, Union

from ..schemas.llm_prompt import *

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

def convert_prompt_for_llama3(json_output: Dict[str, Any], patient_name: Optional[str] = None) -> str:
    # Initialize an empty string for the input transcript
    input_transcript: str = ""
    
    # Create a dictionary to map speaker IDs to speaker numbers
    speaker_map: Dict[str, str] = {}
    
    # Create a modified example with the patient's name
    if patient_name:
        modified_example = MEDICAL_OUTPUT_EXAMPLE.replace(
            '"patient_name": "Tony Stark"', 
            f'"patient_name": "{patient_name}"'
        )
    else:
        modified_example = MEDICAL_OUTPUT_EXAMPLE
    
    # Iterate over the segments in the JSON output
    for segment in json_output["segments"]:
        if segment["speaker"] not in speaker_map:
            speaker_number: str = str(len(speaker_map) + 1)
            speaker_map[segment["speaker"]] = speaker_number
            
        speaker_number = speaker_map[segment["speaker"]]
        input_transcript += f"Speaker {speaker_number}: {segment['text']}\n"

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

async def whisper_diarization(file_url: str): 
    output = replicate.run(
        "thomasmol/whisper-diarization:cbd15da9f839c5f932742f86ce7def3a03c22e2b4171d42823e83e314547003f",
        input={
            "file": file_url,
            "prompt": "LLama, AI, Meta.",
            "file_url": "",
            "language": "vi",
            "translate": False,
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