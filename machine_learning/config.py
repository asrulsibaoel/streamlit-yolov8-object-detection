import os

import dotenv


class Settings:

    amqp_host: str = os.getenv("AMQP_HOST", "localhost")
    amqp_port: str = os.getenv("AMQP_PORT", "guest")
    amqp_username: str = os.getenv("AMQP_USERNAME", "guest")
    amqp_password: str = os.getenv("AMQP_PASSWORD", "5672")
    amqp_exchange: str = os.getenv("AMQP_EXCHANGE", "logs")
    amqp_incoming_routing: str = os.getenv("AMQP_INCOMING_ROUTING", "incoming")
    amqp_outgoing_routing: str = os.getenv("AMQP_OUTGOING_ROUTING", "outgoing")

    recognition_model: str = os.getenv("RECOGNITION_MODEL", "Facenet512")
    face_detection_model: str = os.getenv("FACE_DETECTION_MODEL", "yolov8")

    vector_db_uri: str = os.getenv("VECTOR_DB_URI", "")
    vector_db_secret: str = os.getenv("VECTOR_DB_SECRET", "")
