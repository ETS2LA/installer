import json
import os

filepath = "launcher/settings.json"

def validate_file():
    try:
        if not os.path.exists(filepath):
            with open(filepath, "w") as file:
                json.dump({}, file)
                
        with open(filepath, "r") as file:
            json.load(file)
    except: 
        os.remove(filepath)
        with open(filepath, "w") as file:
            json.dump({}, file)
            
def get(key: str, default=None):
    validate_file()
    with open(filepath, "r") as file:
        data = json.load(file)
        return data.get(key, default)
    return default
    
def set(key: str, value):
    validate_file()
    with open(filepath, "r") as file:
        data = json.load(file)
        data[key] = value
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)