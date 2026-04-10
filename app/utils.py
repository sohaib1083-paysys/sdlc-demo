import os
import uuid
from fastapi import UploadFile

def save_file(file: UploadFile):
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    with open(f"uploads/{filename}", "wb") as f:
        f.write(file.file.read())
    return filename
