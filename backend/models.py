from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Define the SQLAlchemy Base
Base = declarative_base()


class RTSPStream(Base):
    __tablename__ = "rtsp_streams"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)


class RTSPRequestDTO(BaseModel):
    url: str


class RTSPIdRequestDTO(BaseModel):
    rtsp_id: int
