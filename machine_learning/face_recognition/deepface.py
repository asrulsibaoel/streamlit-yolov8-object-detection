import base64
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

from deepface import DeepFace
import numpy as np
from PIL import Image

from machine_learning.database.vector_db import MilvusVectorDB


class FacialAnalysis(object):

    def __init__(self,
                 vector_db: MilvusVectorDB,
                 recognition_model: str = "Facenet512",
                 detection_model: str = "yolov8") -> None:
        self.recognition_model = recognition_model
        self.detection_model = detection_model
        self.vector_client = vector_db

    def create_face_embedding(self, img: Image.Image) -> dict:
        embedding = DeepFace.represent(
            np.asarray(img),
            model_name=self.recognition_model,
            detector_backend=self.detection_model
        )

        return embedding

    def encode_to_base64(self, img: Image.Image):
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return img_str

    def register_face(self, img: Image.Image, label: str) -> bool:
        embedded_face = self.create_face_embedding(img)
        if len(embedded_face) > 1 or len(embedded_face) == 0:
            raise Exception("Multiple Face or no face detected.")

        embedded_face = embedded_face[0]
        metadata = {
            "image": self.encode_to_base64(img),
            "created_at": datetime.now().timestamp()
        }
        return self.vector_client.insert_vector(
            label, embedded_face['embedding'], metadata)

    def recognize(self, img: Image.Image) -> List[Dict[str, Any]]:
        # TODO:
        # search by vector
        # find the best match
        faces = self.create_face_embedding(img)
        predicted_at = datetime.now().strftime("%Y-%m-%d %H:%I:%s")
        known_faces = []
        for face in faces:
            known_face = self.vector_client.search_by_vector(
                face['embedding'], 1
            )[0][0]

            is_known = known_face['distance'] >= 0.7

            result = {
                "indicated_as": known_face['id'] if is_known else "Unknown",
                "is_known": is_known,
                "predicted_at": predicted_at
            }
            known_faces.append(result)
        return known_faces
