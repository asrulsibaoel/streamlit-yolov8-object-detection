FROM ultralytics/ultralytics:latest as base_image

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt
