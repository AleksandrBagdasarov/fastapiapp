import asyncio
import datetime

import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from db.postgres.connector import engine
from db.postgres.models import Notifications, User
from db.redis_processor import MyRedis
from modules.smtp.processor import send_email
from time import time

redis = MyRedis()
local_time_zone = tzlocal.get_localzone_name()
sched = AsyncIOScheduler(timezone=local_time_zone)

UPDATE_DELAY = 600


async def planning_notifications():
    notifications = await redis.get("notifications")
    if notifications:
        for notification_id, notification in notifications.items():
            sched.add_job(
                send_email,
                "date",
                run_date=datetime.datetime.strptime(notification["notify_time"], "%Y-%m-%d %H:%M:%S"),
                args=[notification["email"], notification["title"], notification["body"]],
            )

    await redis.set("last_update_time", {"planning_notifications": time()})


async def collect_notifications():
    last_update_time = get_last_update_time(key="planning_notifications")
    async_session = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)
    async with async_session() as session:

        select_stmt = (
            select(Notifications)
            .with_only_columns(
                Notifications.id,
                Notifications.notify_time,
                Notifications.title,
                Notifications.body,
                User.email,
            )
            .join(User, User.id == Notifications.user_id)
            .where(
                between(
                    Notifications.notify_time,
                    datetime.datetime.utcnow() - datetime.timedelta(seconds=last_update_time),
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=UPDATE_DELAY),
                )
            )
        )
        result = await session.execute(select_stmt)
        notifications = [dict(notification) for notification in result.all()]

    if notifications:
        current_notifications = await redis.get("notifications")
        for i, notification in enumerate(notifications):

            print(f"to redis #{i}", notification)
            current_notifications.update(
                {
                    str(notification["id"]): {
                        "notify_time": notification["notify_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "email": notification["email"],
                        "title": notification["title"],
                        "body": notification["body"],
                    }
                }
            )
        await redis.set("notifications", current_notifications)


def get_last_update_time(key, update_delay=UPDATE_DELAY):
    last_update_time = 0
    last_update = await redis.get("last_update_time")
    if last_update:
        last_update_time = time() - (last_update.get(key) + datetime.timedelta(seconds=update_delay))
    return last_update_time


# todo apscheduler.jobstores.base?
sched.add_job(collect_notifications, "interval", seconds=UPDATE_DELAY, misfire_grace_time=120)
sched.add_job(planning_notifications, "interval", seconds=UPDATE_DELAY, misfire_grace_time=120)

while True:
    sched.start()
    asyncio.get_event_loop().run_forever()
