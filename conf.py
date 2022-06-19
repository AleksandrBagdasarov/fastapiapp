from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
REDIS_HOST = os.getenv("REDIS_HOST")
ENCODING = os.getenv("ENCODING")
SENDGRID_EMAIL = os.getenv("SENDGRID_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MASTER_SECRET_KEY = os.getenv("MASTER_SECRET_KEY")
SALT = os.getenv("SALT")
POSTGRES_CONNECTION_URL = os.getenv("POSTGRES_CONNECTION_URL")


REDIS_URL = f"redis://{REDIS_HOST}"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
