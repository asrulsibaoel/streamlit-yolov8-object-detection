import os

import dotenv

dotenv.load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/database")
