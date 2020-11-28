import uuid

from aiohttp import web

from app import sio
from api.socket.constants import GAME_NS
from models import Notification


async def create(request: web.Request) -> web.Response:
    data = await request.json()
    message = data.get("message", None)
    if message:
        try:
            notification = Notification.create(uuid=uuid.uuid4(), message=message)
            notification.save()
            await sio.emit(
                "Notification.Show",
                {"uuid": str(notification.uuid), "message": notification.message},
                namespace=GAME_NS,
            )
        except:
            return web.HTTPServerError(reason="Failed to create new notification.")
        return web.HTTPOk(text=f"Created new notification with id {notification.uuid}")
    else:
        return web.HTTPBadRequest(reason="Missing mandatory field 'message'")


async def collect(request: web.Request) -> web.Response:
    notifications = [
        {"uuid": str(n.uuid), "message": n.message} for n in Notification.select()
    ]
    return web.json_response(notifications)


async def delete(request: web.Request) -> web.Response:
    uuid = request.match_info.get("uuid", None)
    if uuid:
        try:
            notification = Notification.get_by_id(uuid)
        except Notification.DoesNotExist:
            return web.HTTPNotFound(
                reason="Notification with given uuid was not found."
            )
        notification.delete_instance()
        return web.HTTPOk(text=f"Removed notification with id {notification.uuid}")
    else:
        return web.HTTPBadRequest(reason="Missing uuid.")
