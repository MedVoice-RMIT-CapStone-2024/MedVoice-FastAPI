import pvfalcon
import pvleopard

ACCESS_KEY="<PICOVOICE_ACCESS_KEY>"
AUDIO_PATH="../assets/what-is-this.mp3"
falcon = pvfalcon.create(access_key=ACCESS_KEY)
leopard = pvleopard.create(access_key=ACCESS_KEY)

segments = falcon.process_file(AUDIO_PATH)
# for segment in segments:
#     print(        
#         "{speaker_tag=%d start_sec=%.2f end_sec=%.2f}"
#         % (segment.speaker_tag, segment.start_sec, segment.end_sec)
#     )

transcript, words = leopard.process_file(AUDIO_PATH)
# print(transcript)
# for word in words:
#     print(
#       "{word=\"%s\" start_sec=%.2f end_sec=%.2f confidence=%.2f}"
#       % (word.word, word.start_sec, word.end_sec, word.confidence))

# Initialize an empty dictionary to store the final sentences
sentences = {}
sentences_v2 = []

# Iterate over each speaker segment
for segment in segments:
    # Initialize an empty list to store the words for this speaker segment
    words_for_segment = []

    # Iterate over each word
    for word in words:
        # If the word's start time is within the speaker segment's start and end times, add it to the list
        if segment.start_sec <= word.start_sec <= segment.end_sec:
            words_for_segment.append(word.word)

    # Join the words together to form a sentence and add it to the list along with the speaker tag and timestamps
    sentences_v2.append({
        "speaker_tag": segment.speaker_tag,
        "sentence": " ".join(words_for_segment),
        "start_sec": segment.start_sec,
        "end_sec": segment.end_sec
    })

    # If the speaker tag already exists in the dictionary, append the words to the existing sentence
    if segment.speaker_tag in sentences:
        sentences[segment.speaker_tag] += " " + " ".join(words_for_segment)
    # Otherwise, join the words together to form a sentence and store it in the dictionary
    else:
        sentences[segment.speaker_tag] = " ".join(words_for_segment)

# Print the final sentences
for tag, sentence in sentences.items():
    print(f"Speaker {tag}: {sentence}")

print("\n-------------------\n")

# Print the final sentences
for sentence_info in sentences_v2:
    print(f'["start_sec": {sentence_info["start_sec"]}, "end_sec": {sentence_info["end_sec"]}] Speaker {sentence_info["speaker_tag"]}: {sentence_info["sentence"]}')

# Open the file in write mode
with open('falcon-output.txt', 'w') as f:
    # Write the sentences to the file
    for tag, sentence in sentences.items():
        f.write(f"Speaker {tag}: {sentence}\n")

    f.write("\n-------------------\n")

    for sentence_info in sentences_v2:
        f.write(f'["start_sec": {sentence_info["start_sec"]}, "end_sec": {sentence_info["end_sec"]}] Speaker {sentence_info["speaker_tag"]}: {sentence_info["sentence"]}\n')

