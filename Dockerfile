FROM ultralytics/ultralytics:latest as base_image

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt


FROM base_image as frontend

COPY . /app/
ENTRYPOINT ["streamlit"]
