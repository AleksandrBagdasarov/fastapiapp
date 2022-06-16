from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import declarative_base
from db.postgres.connector import engine
from sqlalchemy import Column, Index, column, func, desc
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, NUMERIC, DATE, JSON, BOOLEAN, INTEGER, TIMESTAMP
from uuid import uuid4
import enum


Base = declarative_base()


class AdminRoles(enum.Enum):
    root = 1
    admin = 2
    moderator = 3


class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        Index("idx_user_id", "id"),
        Index("idx_user_lower_email", func.lower(column("email"))),
    )

    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(VARCHAR, nullable=False, unique=True)
    firstname = Column(VARCHAR, nullable=True)
    lastname = Column(VARCHAR, nullable=True)
    avatar = Column(VARCHAR, nullable=True)
    password = Column(VARCHAR, nullable=False)
    blocked = Column(BOOLEAN, default=False)


class Notifications(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        Index("idx_notifications_id", "id"),
        Index("idx_notifications_lower_title", func.lower(column("title"))),
    )

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    title = Column(VARCHAR, nullable=False, unique=True)
    body = Column(VARCHAR, nullable=True)
    notify_time = Column(TIMESTAMP, nullable=False)


class AdminUsers(Base):
    __tablename__ = "admin_users"

    id = Column(UUID, primary_key=True, default=uuid4)
    role = Column(Enum(AdminRoles))
    email = Column(VARCHAR, nullable=False, unique=True)
    firstname = Column(VARCHAR, nullable=True)
    lastname = Column(VARCHAR, nullable=True)
    avatar = Column(VARCHAR, nullable=True)
    password = Column(VARCHAR, nullable=False)
    blocked = Column(BOOLEAN, default=False)


async def create_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_models())
