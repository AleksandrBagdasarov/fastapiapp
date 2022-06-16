import pytest
from sqlalchemy.cimmutabledict import immutabledict

from db.postgres.models import User, Notifications, AdminRoles
from db.postgres.connector import engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from modules.user.auth.utils import sign_jwt
from db.redis_processor import MyRedis


redis = MyRedis()


@pytest.mark.asyncio
class UserSetup:

    storage = {}

    @pytest.fixture(scope="session", autouse=True)
    async def init(self, client):
        await self.cleanup()

        self.storage["client"] = client

    @staticmethod
    async def cleanup():
        tables_to_clean = (
            Notifications,
            User
        )

        async with engine.connect() as conn:
            for table in tables_to_clean:
                stmt = delete(table).filter(table.id.isnot(None))
                await conn.execute(stmt)
            await conn.commit()

    def request(self, endpoint, method, json=None, **kwargs):
        response = self.storage["client"].request(
            method=method,
            url=endpoint,
            json=json,
            *kwargs
        )
        return response

    @pytest.fixture
    async def new_user(self):

        async def create(
                email="test@example.com",
                password="Example#1",
                firstname="test",
                lastname="test",
        ):
            self.request(
                endpoint="/signup",
                method="POST",
                json={
                    "email": email,
                    "password": password,
                    "firstname": firstname,
                    "lastname": lastname,
                },
            )

            self.request(
                endpoint="/login",
                method="POST",
                json={
                    "email": email,
                    "password": password
                }
            )

            async_session = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )
            async with async_session() as session:
                result = await session.execute(
                    select(User)
                    .where(
                        User.email == email
                    )
                )
                user = result.first()["User"]

            token = await sign_jwt(user_id=user.id)
            await redis.set(
                user.id, {
                    "token": token
                },
                ttl=600
            )
            self.storage["client"].headers.update(
                {"Authorization": f"Bearer {token}"}
            )

            return user
        yield create

        await self.cleanup()

    async def signup(
            self,
            email: str,
            password: str,
            firstname: str = None,
            lastname: str = None
    ):
        response = self.request(
            endpoint="/signup",
            method="POST",
            json={
                "email": email,
                "password": password,
                "firstname": firstname,
                "lastname": lastname,
            }
        )
        return response

    async def signin(self, email: str, password: str):
        response = self.request(
            endpoint="/signin",
            method="POST",
            json={
                "email": email,
                "password": password
            }
        )
        return response

    async def logout(self):
        response = self.request(
            endpoint="/logout",
            method="GET"
        )
        return response

    async def create_notification(
            self,
            title: str,
            notify_time: str,
            body: str = "",
    ):
        response = self.request(
            endpoint="/notifications/create",
            method="POST",
            json={
                "title": title,
                "notify_time": notify_time,
                "body": body,
            }
        )
        return response

    async def delete_notifications(
            self,
            notification_ids: list
    ):
        response = self.request(
            endpoint="/notifications/delete",
            method="POST",
            json={
                "notification_ids": notification_ids,
            }
        )
        return response

    async def update_notification(
            self,
            data
    ):
        response = self.request(
            endpoint="/notifications/update",
            method="POST",
            json=data
        )
        return response

    async def get_notifications(
            self,
            limit=10,
            offset=0
    ):
        query = f"?limit={limit}&offset={offset}"
        response = self.request(
            endpoint=f"/notifications{query}",
            method="GET"
        )
        return response

    async def get_profile(self):
        response = self.request(
            "/profile",
            method="GET"
        )
        return response

    async def edit_profile(
            self,
            firstname: str = "",
            lastname: str = "",
            email: str = "",
            password: str = "",
    ):
        payload = {
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "password": password,
            }

        response = self.request(
            "/profile/edit",
            method="POST",
            json={k: v for k, v in payload.items() if v}
        )
        return response


