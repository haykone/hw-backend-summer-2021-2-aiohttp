import asyncio
import typing
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import (Message, Update, UpdateMessage,
                                          UpdateObject)
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        try:
            await self._get_long_poll_service()
            self.poller = Poller(app.store)
            await self.poller.start()
            self.logger.info("VK API connected and poller started")
        except Exception as e:
            self.logger.error(f"Failed to connect to VK API: {e}")

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()
        self.logger.info("VK API disconnected")

    async def _get_long_poll_service(self):
        params = {
            "group_id": self.app.config.bot.group_id,
            "access_token": self.app.config.bot.token,
        }
        url = self._build_query("https://api.vk.com",
                                "groups.getLongPollServer", params)
        async with self.session.get(url) as response:
            data = await response.json()
            results = data["response"]
            self.key = results["key"]
            self.server = results["server"]
            self.ts = results["ts"]

    async def poll(self) -> list[Update]:
        params = {
            "act": "a_check",
            "key": self.key,
            "ts": self.ts,
            "wait": 25,
        }
        async with self.session.get(self.server, params=params) as response:
            data = await response.json()
            self.ts = data["ts"]
            updates = []
            for raw_update in data.get("updates", []):
                if raw_update["type"] == "message_new":
                    msg = raw_update["object"]["message"]

                    if isinstance(msg, dict):
                        text = msg.get("text", "")
                    else:
                        str(msg)
                    updates.append(Update(
                        type="message_new",
                        object=UpdateObject(
                            message=UpdateMessage(
                                from_id=msg["from_id"],
                                text=text,
                                id=msg["id"]
                            )
                        )
                    ))
            return updates

    async def send_message(self, message: Message) -> None:
        params = {
            "user_id": message.user_id,
            "message": message.text,
            "random_id": 0,
            "access_token": self.app.config.bot.token,
        }
        url = self._build_query("https://api.vk.com", "messages.send", params)
        async with self.session.get(url) as response:
            await response.json()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        base = urljoin(host.rstrip("/") + "/", "method/" + method)
        return f"{base}?{urlencode(params)}"
