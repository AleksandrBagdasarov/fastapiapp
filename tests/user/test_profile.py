from tests import UserSetup
from fastapi import status


class TestProfile(UserSetup):
    async def test_get_profile(self, new_user):
        await new_user()
        response = await self.get_profile()
        assert response.status_code == status.HTTP_200_OK

    async def test_update_img(self, new_user):
        raise NotImplementedError

    async def test_edit_personal_info(self, new_user):
        await new_user()
        response = await self.edit_profile(
            firstname="editedfirstname",
            lastname="editedlastname",
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_reset_password(self, new_user):
        raise NotImplementedError

    async def test_reset_email(self, new_user):
        raise NotImplementedError
