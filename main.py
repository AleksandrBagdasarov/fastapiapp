import uvicorn

from fastapi import FastAPI, Request, Depends, UploadFile
from modules.user.auth.processor import signup, signin, logout
from modules.notifications.processor import (
    get_notifications,
    create_notification,
    update_notification,
    delete_notifications,
)
from modules.user.auth.utils import JWTBearer
from modules.user.pofile import get_profile, edit_profile, save_avatar

app = FastAPI()


@app.post("/signup")
async def signup_handler(data: Request):
    """future (request: Request)"""
    result = await signup(data)
    return result


@app.post("/signin")
async def signin_handler(data: Request):
    """future (request: Request)"""
    result = await signin(data)
    return result


@app.get("/logout", dependencies=[Depends(JWTBearer())])
async def logout_handler(data: Request):
    """future (request: Request)"""
    result = await logout(data)
    return result


@app.get("/profile", dependencies=[Depends(JWTBearer())])
async def profile_handler(data: Request):
    result = await get_profile(data)
    return result


@app.post("/profile/edit", dependencies=[Depends(JWTBearer())])
async def profile_handler(data: Request):
    result = await edit_profile(data)
    return result


@app.post("/profile/edit/avatar", dependencies=[Depends(JWTBearer())])
async def profile_handler(data: Request):
    result = await save_avatar(data)
    return result


@app.get("/notifications", dependencies=[Depends(JWTBearer())])
async def notifications_handler(request: Request, limit: str, offset: str):
    result = await get_notifications(request, limit, offset)
    return result


@app.post("/notifications/create", dependencies=[Depends(JWTBearer())])
async def notifications_create_handler(data: Request):
    """future (request: Request)"""
    result = await create_notification(data)
    return result


@app.post("/notifications/update", dependencies=[Depends(JWTBearer())])
async def notifications_update_handler(data: Request):
    """future (request: Request)"""
    result = await update_notification(data)
    return result


@app.post("/notifications/delete", dependencies=[Depends(JWTBearer())])
async def notifications_delete_handler(data: Request):
    """future (request: Request)"""
    result = await delete_notifications(data)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
