# Picovoice Models
import pvfalcon, pvleopard

def picovoice_models(temp_audio_path: str, access_key: str):
    falcon = pvfalcon.create(access_key=access_key)
    leopard = pvleopard.create(access_key=access_key)

    segments = falcon.process_file(temp_audio_path)
    transcript, words = leopard.process_file(temp_audio_path)

    sentences = {}
    sentences_v2 = []

    for segment in segments:
        words_for_segment = [word.word for word in words if segment.start_sec <= word.start_sec <= segment.end_sec]

        sentences_v2.append({
            "speaker_tag": segment.speaker_tag,
            "sentence": " ".join(words_for_segment),
            "start_sec": segment.start_sec,
            "end_sec": segment.end_sec
        })

        if segment.speaker_tag in sentences:
            sentences[segment.speaker_tag] += " " + " ".join(words_for_segment)
        else:
            sentences[segment.speaker_tag] = " ".join(words_for_segment)

    return {"sentences": sentences, "sentences_v2": sentences_v2}