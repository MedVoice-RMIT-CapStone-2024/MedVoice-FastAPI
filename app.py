import replicate
from pygments import highlight, lexers, formatters
import os

output = replicate.run(
    "thomasmol/whisper-diarization:b9fd8313c0d492bf1ce501b3d188f945389327730773ec1deb6ef233df6ea119",
    input={
        "file": "https://storage.googleapis.com/medvoice-sgp-audio-bucket/what-is-this-what-are-these-63645.mp3",
        "prompt": "Mark and Lex talking about AI.",
        "file_url": "",
        "num_speakers": 2,
        "group_segments": True,
        "offset_seconds": 0,
        "transcript_output_format": "both"
    }
)
print(output)