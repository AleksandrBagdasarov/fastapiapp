from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
REDIS_HOST = os.getenv('REDIS_HOST')
ENCODING = os.getenv('ENCODING')
EMAIL_FOR_SMTP = os.getenv('EMAIL_FOR_SMTP')
MASTER_SECRET_KEY = os.getenv('MASTER_SECRET_KEY')
SALT = os.getenv('SALT')
POSTGRES_CONNECTION_URL = os.getenv('POSTGRES_CONNECTION_URL')


REDIS_URL = f"redis://{REDIS_HOST}"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
