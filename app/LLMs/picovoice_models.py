# Picovoice Models
# import pvfalcon, pvleopard

# def picovoice_models(temp_audio_path: str, access_key: str):
#     falcon = pvfalcon.create(access_key=access_key)
#     leopard = pvleopard.create(access_key=access_key)

#     segments = falcon.process_file(temp_audio_path)
#     transcript, words = leopard.process_file(temp_audio_path)

#     sentences = {}
#     sentences_v2 = []

#     for segment in segments:
#         words_for_segment = [word.word for word in words if segment.start_sec <= word.start_sec <= segment.end_sec]

#         sentences_v2.append({
#             "speaker_tag": segment.speaker_tag,
#             "sentence": " ".join(words_for_segment),
#             "start_sec": segment.start_sec,
#             "end_sec": segment.end_sec
#         })

#         if segment.speaker_tag in sentences:
#             sentences[segment.speaker_tag] += " " + " ".join(words_for_segment)
#         else:
#             sentences[segment.speaker_tag] = " ".join(words_for_segment)

#     return {"sentences": sentences, "sentences_v2": sentences_v2}


### Move this endpoint to main.py if you want to use it ###

# @app.post("/process_audio")
# async def process_audio(user_id: str, file_name: str, access_key="XqSUBqySs7hFkIfYiPZtx27L59XDKnzZzAM7rU5pKmjGGFyDf+6bvQ=="):
#     try:
#         # Download the file specified by 'user_id' and 'file_name' asynchronously
#         audio_file = await download_and_upload_audio_file(user_id, file_name)

#         # Extract the new file name and file id from the downloaded file's details
#         audio_file_path, file_id = audio_file['new_file_name'], audio_file['file_id']

#         # Use the Picovoice models to process the audio file and generate outputs
#         picovoice_outputs = picovoice_models(audio_file_path, access_key)

#         # Save the 'sentences_v2' output from Picovoice to a file, and get the path of the saved file
#         transcript_file_path = save_json_to_text(picovoice_outputs["sentences_v2"], file_id)

#         # Upload the output file to a cloud storage bucket
#         upload_file_to_bucket(cloud_details['project_id'], cloud_details['bucket_name'], transcript_file_path, transcript_file_path)
        
#         # Remove the audio file and output file from the local directory
#         os.remove(audio_file_path)
#         os.remove(transcript_file_path)

#         return {
#             "sentences": picovoice_outputs["sentences"],
#             "sentences_v2": picovoice_outputs["sentences_v2"],
#             "file_id": file_id
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))