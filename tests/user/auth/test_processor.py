from tests import UserSetup
from fastapi import status


class TestAuth(UserSetup):
    async def test_signup(self):
        response = await self.signup(email="example@mai.com", password="Example#1", firstname="John", lastname="Doe")
        assert response.status_code == status.HTTP_200_OK

    async def test_signin(self, new_user):
        email = "test@example.com"
        pwd = "Example#1"
        await new_user(
            email=email,
            password=pwd,
        )

        response = await self.signin(email=email, password=pwd)
        assert response.status_code == status.HTTP_200_OK

    async def test_logout(self, new_user):
        await new_user()
        response = await self.logout()
        assert response.status_code == status.HTTP_200_OK
        response = await self.logout()
        assert response.status_code == status.HTTP_403_FORBIDDEN
