import replicate

async def llama_2(output):

    result = ''
    # The meta/llama-2-70b-chat model can stream output as it's running.
    for event in replicate.stream(
        "meta/llama-2-70b-chat",
        input={
            "top_k": 0,
            "top_p": 1,
            "prompt": f"""Summarize the transcript organized by key topics.
                If someone has said something important, mention it as: '<Name of the person> made a significant contribution by stating that <important statement>'
                At the bottom, list out the follow up actions if discussed
                ----
                Transcript: {output}
            """,
            "temperature": 0.5,
            "system_prompt": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.",
            "length_penalty": 1,
            "max_new_tokens": 500,
            "min_new_tokens": -1,
        },
    ):
        result += str(event)
    print("\nLlama 2 Result: " + result)
    return result

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