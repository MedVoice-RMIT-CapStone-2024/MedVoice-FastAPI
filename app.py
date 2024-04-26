import replicate
from pygments import highlight, lexers, formatters
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def pretty_print_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, 
        lexers.JsonLexer(), 
        formatters.TerminalFormatter()
    )
    print(colorful_json)

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
pretty_print_json(output)