import uuid

from fastapi import Request
import re
from fastapi import responses, status
from db.postgres.models import User
from db.postgres.connector import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.redis_processor import MyRedis
from modules.user.auth.utils import get_hashed_pwd, sign_jwt, remove_token


redis = MyRedis()


async def signup(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    credential_errors = []
    if email and password:
        pattern = r"(^[a-zA-Z0-9_+.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.search(pattern, email):
            credential_errors.append(
                "Email is invalid."
            )
        if len(password) < 8:
            credential_errors.append(
                "Password must be more than 8 characters."
            )

        if re.search('[0-9]', password) is None:
            credential_errors.append(
                "Make sure your password has a number in it."
            )

        if re.search('[A-Z]', password) is None:
            credential_errors.append(
                "Make sure your password has a capital letter in it."
            )
    else:
        credential_errors.append(
            "Email or password not specified."
        )

    # todo firstname validator
    # todo lastname validator

    message = "Registration completed successfully!"
    signup_status = status.HTTP_200_OK
    if credential_errors:
        message = "\n".join(credential_errors)
        signup_status = status.HTTP_400_BAD_REQUEST
    else:
        hashed_pwd = await get_hashed_pwd(password)
        async_session = sessionmaker(
            engine, expire_on_commit=True, class_=AsyncSession
        )
        async with async_session() as session:
            user = User(
                id=str(uuid.uuid4()),
                password=hashed_pwd,
                email=email,
                firstname=firstname,
                lastname=lastname,
                blocked=False
            )
            session.add_all([user])
            await session.commit()

    return responses.JSONResponse(
        {
            "message": message
        },
        status_code=signup_status
    )


async def signin(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    hashed_pwd = await get_hashed_pwd(password)

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
    if not user:
        return responses.JSONResponse(
            {
                "message": "User not found."
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    elif user.blocked:
        return responses.JSONResponse(
            {
                "message": "User was blocked."
            },
            status_code=status.HTTP_403_FORBIDDEN
        )
    elif user.password != hashed_pwd:
        return responses.JSONResponse(
            {
                "message": "Wrong password."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )
    else:
        token = await sign_jwt(user_id=user.id)
        await redis.set(
            user.id, {
                "token": token
            },
            ttl=600
        )

        return responses.JSONResponse(
            {
                "message": "Success!",
                "token": token
            },
            status_code=status.HTTP_200_OK
        )


async def logout(request: Request):
    await remove_token(request)
    return responses.JSONResponse(
        {
            "message": "User logout success."
        },
        status_code=status.HTTP_200_OK
    )
