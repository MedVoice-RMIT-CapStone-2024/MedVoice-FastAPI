from enum import Enum
from pydantic import BaseModel

class FileExtension(str, Enum):
    txt = "txt"
    json = "json"

class AudioExtension(str, Enum):
    mp3 = "mp3"
    wav = "wav"
    m4a = "m4a"

class SourceType(str, Enum):
    json = "json"
class Question(BaseModel):
    question: str
    source_type: SourceType