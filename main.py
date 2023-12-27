from fastapi import FastAPI, Body, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid, os, base64


import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import UploadFile

import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    STATICFILES_ENDPOINT: str
    STATICFILES_DIR: str
    
    SERVER_HOST: str
    SERVER_PORT: str

    SERVER_URL: Optional[str] = None
    @validator("SERVER_URL", pre=True)
    def assemble_server_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"https://{values.get('SERVER_HOST')}{values.get('STATICFILES_ENDPOINT')}"
    
    class Config:
        case_sensitive = True
        env_file='.env'
        env_file_encoding='utf-8'

settings = Settings()

import os
if not os.path.exists(settings.STATICFILES_DIR):
    os.makedirs(settings.STATICFILES_DIR)



if not os.path.exists(settings.STATICFILES_DIR):
    os.makedirs(settings.STATICFILES_DIR)

def save_upload_file(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix, dir= settings.STATICFILES_DIR) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path


############# App definition
app = FastAPI(
    title= "Storage service", openapi_url=f"/openapi.json"
)


@app.post("/upload")
def create(
    *,
    file: UploadFile = File(...),
) -> str:
    """
    Create new media file.
    """
    path = save_upload_file(file)

    return settings.SERVER_URL + "/" + path.name


@app.post("/upload/base64")
def upload_file_base64(
    content: str = Body(...), 
    ext: str = Body(...),
):
    filename = ""
    path: str

    while True:
        filename = str(uuid.uuid4()) + "." + ext
        path = settings.STATICFILES_DIR, filename
        if not os.path.exists(os.path.join(*path)):
            break
    
    with open(os.path.join(settings.STATICFILES_DIR, filename), "wb") as f:
        f.write(base64.b64decode(content))


    return settings.SERVER_URL + "/" + filename


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(settings.STATICFILES_ENDPOINT, StaticFiles(directory= settings.STATICFILES_DIR), name="static")