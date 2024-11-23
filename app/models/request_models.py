from enum import Enum
from pydantic import BaseModel

### Enum models ###
class FileExtension(str, Enum):
    txt = "txt"
    json = "json"

class SourceType(str, Enum):
    pdf = "pdf"
    json = "json"

class AudioExtension(str, Enum):
    mp3 = "mp3"
    wav = "wav"
    m4a = "m4a"

### Base models ###
class Question(BaseModel):
    question: str
    source_type: SourceType