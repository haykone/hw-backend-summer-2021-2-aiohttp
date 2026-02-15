import base64
import typing

from aiohttp import web
from aiohttp.web import View as AiohttpView
from aiohttp.web_app import Application as AiohttpApplication
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

from app.store import Store, setup_store
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: typing.Optional[Config] = None
    store: typing.Optional[Store] = None


def setup_app(config_path: str) -> Application:
    app = Application()
    setup_logging(app)

    setup_config(app, config_path)

    if hasattr(app.config, 'session') and app.config.session:
        secret_key = base64.urlsafe_b64decode(app.config.session.key)
    else:
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)

    setup_session(app, EncryptedCookieStorage(secret_key))

    setup_routes(app)

    setup_store(app)

    setup_middlewares(app)

    return app


class View(AiohttpView):
    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def database(self):
        return self.store.database

    @property
    def config(self) -> Config:
        return self.request.app.config
