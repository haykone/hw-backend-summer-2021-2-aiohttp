import typing

from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            user_id = update.object.message.from_id

            reply = Message(
                user_id=user_id,
                text="Привет! Я готов к викторине. Пока что я умею только "
                "повторять это сообщение."
            )

            await self.app.store.vk_api.send_message(reply)
