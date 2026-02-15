import typing

from aiohttp.web import Application as AiohttpApplication

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app
        self.database = Database()
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.quiz.accessor import QuizAccessor
        from app.store.vk_api.accessor import VkApiAccessor

        self.vk_api = VkApiAccessor(app)
        self.admins = AdminAccessor(app)
        self.quizzes = QuizAccessor(app)
        self.bots_manager = BotManager(app)

    async def connect(self):
        await self.vk_api.connect(self.app)

        admin_cfg = self.app.config.admin
        existing = await self.admins.get_by_email(admin_cfg.email)
        if not existing:
            await self.admins.create_admin(
                email=admin_cfg.email,
                password=admin_cfg.password
            )

    async def disconnect(self):
        await self.vk_api.disconnect(self.app)


async def _on_startup(app: AiohttpApplication):
    await app.store.connect()


async def _on_cleanup(app: AiohttpApplication):
    await app.store.disconnect()


def setup_store(app: "Application") -> None:
    app.store = Store(app)
    app.database = app.store.database
    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_on_cleanup)
