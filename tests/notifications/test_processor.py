from tests import UserSetup
from fastapi import status
from datetime import datetime, timedelta
from conf import DATETIME_FORMAT
import json


class TestNotifications(UserSetup):
    async def test_get_notification(self, new_user):
        # todo create db migration
        await new_user()
        response = await self.get_notifications()
        assert response.status_code == status.HTTP_200_OK

    async def test_create_notification(self, new_user):
        await new_user()
        notify_time = (datetime.utcnow() + timedelta(days=1)).strftime(DATETIME_FORMAT)

        response = await self.create_notification(title="Test Title", notify_time=notify_time, body="Test Body")
        assert response.status_code == status.HTTP_200_OK

    async def test_update_notification(self, new_user):
        await new_user()
        notify_time = (datetime.utcnow() + timedelta(days=1)).strftime(DATETIME_FORMAT)

        notification = await self.create_notification(title="Test Title", notify_time=notify_time, body="Test Body")
        payload = notification.json()
        notification_id = payload["notification_id"]
        notify_update_time = (datetime.utcnow() + timedelta(days=2)).strftime(DATETIME_FORMAT)
        update_data = {"notification_id": notification_id, "notify_time": notify_update_time, "title": "Another Title"}

        response = await self.update_notification(update_data)
        assert response.status_code == status.HTTP_200_OK

    async def test_delete_notification(self, new_user):
        await new_user()
        notify_time = (datetime.utcnow() + timedelta(days=1)).strftime(DATETIME_FORMAT)

        await self.create_notification(  # todo create db migration
            title="Test Title 1", notify_time=notify_time, body="Test Body"
        )
        await self.create_notification(  # todo create db migration
            title="Test Title 2", notify_time=notify_time, body="Test Body"
        )

        # todo or create fixture

        response = await self.get_notifications()

        response_data = response.json()
        notification_id = response_data["notifications"][0]["notification_id"]
        response = await self.delete_notifications([notification_id])

        assert response.status_code == status.HTTP_200_OK
