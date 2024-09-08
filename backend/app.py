
from fastapi import FastAPI, Depends, HTTPException
from requests import Session
import uvicorn


from database import get_db
from models import RTSPRequestDTO, RTSPStream


# FastAPI app
app = FastAPI()


@app.post("/streams/")
def add_stream(rtsp_url: RTSPRequestDTO, db: Session = Depends(get_db)):
    # Check if the URL is already in the database
    print(rtsp_url)
    existing_stream = db.query(RTSPStream).filter(
        RTSPStream.url == rtsp_url.url).first()
    if existing_stream:
        raise HTTPException(
            status_code=409, detail="Stream URI already registered.")

    # Add the new stream to the database
    new_stream = RTSPStream(url=rtsp_url.url)
    db.add(new_stream)
    db.commit()
    db.refresh(new_stream)
    return new_stream


@app.get("/streams/")
def get_streams(db: Session = Depends(get_db)):
    streams = db.query(RTSPStream).all()
    return streams


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
