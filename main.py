from fastapi import FastAPI, UploadFile
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import Session, declarative_base
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin
import os

app = FastAPI()
Base = declarative_base()
engine = create_engine(os.environ['DATABASE_URL']) # use a postgres database for database persistance

media_path = "media/files" # no leading forward slash indicates this path is relative to the projects directory
media_url = "/media/" # must have leading and trailing forward slashes

class Uploads(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True)
    file = Column(FileType(storage=FileSystemStorage(path=media_path)))

# Create database and table
Base.metadata.create_all(engine)

app.mount(media_url, StaticFiles(directory=media_path), name="media") # serve files from the predfined media_path at media_path

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/upload/")
def create_upload_file(file: UploadFile):
    upload = Uploads(file=file)
    with Session(engine) as session:
        session.add(upload)
        session.commit()
        return {"file_url": urljoin(media_url, upload.file.name)} # return the url to the uploaded file relative to the root of the domain