from sqlalchemy.ext.asyncio import create_async_engine
from conf import POSTGRES_CONNECTION_URL
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    POSTGRES_CONNECTION_URL,
    poolclass=NullPool,
)
