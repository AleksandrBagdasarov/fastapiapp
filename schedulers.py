from db.redis_processor import MyRedis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.smtp.processor import send_email
import asyncio
from db.postgres.models import Notifications
import datetime
from db.postgres.connector import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import between


redis = MyRedis()
sched = AsyncIOScheduler()


async def planning_notifications():
    notifications = await redis.get("notifications")
    if notifications:
        for notification_id, notification in notifications.items():
            sched.add_job(
                send_email,
                "date",
                run_date=notification["notify_time"],
                args=[notification["email"], notifications["title"], notification["body"]],
            )


async def collect_notifications():
    async_session = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)
    async with async_session() as session:
        select_stmt = select(Notifications).where(
            between(
                Notifications.notify_time,
                datetime.datetime.utcnow(),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=120),
            )
        )
        result = await session.execute(select_stmt)
        notifications = [notification["Notifications"] for notification in result.all()]
    if notifications:
        current_notifications = await redis.get("notifications")
        for notification in notifications:
            current_notifications.update(
                {
                    "notification_id": {
                        "notify_time": notification.notify_time,
                        "email": notification.email,
                        "title": notification.title,
                        "body": notification.body,
                    }
                }
            )
        await redis.set("notifications", current_notifications)


sched.add_job(planning_notifications, "interval", minutes=2)

while True:
    sched.start()
    asyncio.get_event_loop().run_forever()
