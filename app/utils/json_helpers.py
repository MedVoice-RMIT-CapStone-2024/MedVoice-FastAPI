import json
from pygments import highlight, lexers, formatters
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.patient import PatientCreate

def pretty_print_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, 
        lexers.JsonLexer(), 
        formatters.TerminalFormatter()
    )
    # print(colorful_json)
    return colorful_json

def remove_json_metadata(data):
    """
    Recursively processes the JSON data to remove metadata like 'type' and 'properties',
    returning a simplified dictionary containing only the key-value pairs.
    """
    if isinstance(data, dict):
        # If the dictionary has 'properties' key, process its value
        if "properties" in data:
            return remove_json_metadata(data["properties"])
        elif "value" in data:
            return remove_json_metadata(data["value"])
        else:
            # Process each key-value pair in the dictionary
            return {key: remove_json_metadata(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Process each item in the list
        return [remove_json_metadata(item) for item in data]
    else:
        # Base case: return the data as is (typically for primitive data types)
        return data
