from fastapi import Request, status, responses, File
from modules.user.auth.utils import decode_jwt, token_from_request
from db.postgres.connector import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.postgres.models import User
import os


async def get_profile(request: Request):
    token_data = decode_jwt(token_from_request(request))
    user_id = token_data["user_id"]

    async_session = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.first()["User"]

    return responses.JSONResponse(
        {"firstname": user.firstname, "lastname": user.lastname, "email": user.email, "avatar": user.avatar},
        status_code=status.HTTP_200_OK,
    )


async def edit_profile(request: Request):
    # todo email validation for password reset or email reset
    token_data = decode_jwt(token_from_request(request))
    user_id = token_data["user_id"]
    payload = await request.json()

    accepted_field_for_update = ("firstname", "lastname", "password", "email")
    accepted_update_values = {k: v for k, v in payload.items() if k in accepted_field_for_update}

    async_session = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)

    async with async_session() as session:
        stmt = update(User).values(accepted_update_values).where(User.id == user_id)
        await session.execute(stmt)
        await session.commit()

    return responses.JSONResponse({"message": "User was updated."}, status_code=status.HTTP_200_OK)


async def save_avatar(request: Request):
    token_data = decode_jwt(token_from_request(request))
    user_id = token_data["user_id"]
    cwd = os.getcwd()
    print(cwd)
    file = File(request)
    full_path = "/fastApiProject/src/assets/img"

    # todo check that file realy image and have correct format and size and weight
    with open(f"{full_path}/{user_id}", "wb") as f:
        f.write(file)

    return responses.JSONResponse({"message": "Avatar was uploaded."}, status_code=status.HTTP_200_OK)
