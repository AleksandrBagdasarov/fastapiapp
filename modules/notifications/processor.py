from fastapi import Request, responses, status
from urllib import parse
from db.postgres.models import Notifications
from db.postgres.connector import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
import uuid
from modules.user.auth.utils import decode_jwt, token_from_request
import datetime
from conf import DATETIME_FORMAT


async def get_notifications(request: Request, limit, offset):
    token_data = decode_jwt(token_from_request(request))
    async_session = sessionmaker(
        engine, expire_on_commit=True, class_=AsyncSession
    )
    async with async_session() as session:
        select_stmt = (
            select(Notifications)
            .where(
                Notifications.user_id == token_data["user_id"]
            )
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(select_stmt)
        notifications = [
            notification["Notifications"] for notification in result.all()
        ]

        payload = []
        for notification in notifications:
            payload.append(
                {
                    "notification_id": str(notification.id),
                    "title": notification.title,
                    "body": notification.body,
                    "notify_time": notification.notify_time.strftime(DATETIME_FORMAT),
                }
            )
        notifications_num = len(payload)
        return responses.JSONResponse(
            {
                "message": f"Got {notifications_num} notifications.",
                "notifications": payload
            },
            status_code=status.HTTP_200_OK
        )


async def create_notification(request: Request):
    # todo timezone
    token_data = decode_jwt(token_from_request(request))
    async_session = sessionmaker(
        engine, expire_on_commit=True, class_=AsyncSession
    )
    payload = await request.json()
    notification_id = str(uuid.uuid4())
    async with async_session() as session:
        notification = Notifications(
            id=notification_id,
            user_id=token_data["user_id"],
            notify_time=datetime.datetime.strptime(payload["notify_time"], "%Y-%m-%d %H:%M:%S"),
            title=payload["title"],
            body=payload.get("body")

        )
        session.add_all([notification])
        await session.commit()
    return responses.JSONResponse(
        {
            "message": "Notification was created.",
            "notification_id": notification_id
        },
        status_code=status.HTTP_200_OK
    )


async def update_notification(request: Request):

    # todo timezone
    token_data = decode_jwt(token_from_request(request))
    payload = await request.json()

    if payload.get("notify_time"):
        payload["notify_time"] = datetime.datetime.strptime(payload["notify_time"], "%Y-%m-%d %H:%M:%S")

    user_id = token_data["user_id"]
    notification_id = payload["notification_id"]

    update_values = {
        k: v for k, v in payload.items() if k in (
            "title", "body", "notify_time"
        )
    }
    # todo validation columns

    async with engine.connect() as conn:
        select_stmt = (
            select(Notifications.user_id)
            .where(
                Notifications.id == notification_id
            )
        )
        result = await conn.execute(select_stmt)
        notification_user_id = result.scalars().first()

        await conn.commit()

        if notification_user_id == user_id:

            async with engine.connect() as conn:
                update_stmt = (
                    update(Notifications)
                    .where(
                        Notifications.id == user_id
                    )
                    .values(update_values)
                    .execution_options(synchronize_session="fetch")

                )
                await conn.execute(update_stmt) # todo does not working WTF?
                await conn.commit()
        else:
            return responses.JSONResponse(
                {
                    "message": "Notification does not belong to the user."
                },
                status_code=status.HTTP_403_FORBIDDEN
            )

    return responses.JSONResponse(
        {
            "message": "Notification was updated.",
            "notification_id": notification_id
        },
        status_code=status.HTTP_200_OK

    )


async def delete_notifications(request: Request):

    token_data = decode_jwt(token_from_request(request))
    payload = await request.json()
    user_id = token_data["user_id"]
    request_notification_ids = payload["notification_ids"]

    async_session = sessionmaker(
        engine, expire_on_commit=True, class_=AsyncSession
    )

    async with async_session() as session:
        result = await session.execute(
            select(Notifications)
            .where(
                Notifications.id.in_(request_notification_ids)
            )
        )
        accepted_notification_ids = [
            n["Notifications"].id for n in result.all()
            if n["Notifications"].user_id == user_id
        ]


        if accepted_notification_ids:
            # delete(Notifications).filter(Notifications.id == notification_id)
            stmt = delete(Notifications).filter(Notifications.id.in_(accepted_notification_ids))
            await session.execute(stmt)
            await session.commit()
        else:
            return responses.JSONResponse(
                {
                    "message": "Notification does not belong to the user."
                },
                status_code=status.HTTP_403_FORBIDDEN
            )
    return responses.JSONResponse(
        {
            "message": "Notification was deleted.",
        },
        status_code=status.HTTP_200_OK
    )
