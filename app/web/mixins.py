from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp_session import get_session


class AuthRequiredMixin:
    """Mixin для проверки авторизации: сессия должна содержать admin."""

    async def check_auth(self):
        """
        Проверяет авторизацию, при успехе возвращает сессию. 
        Иначе — HTTPUnauthorized.
        """
        session = await get_session(self.request)
        if not session or "admin" not in session:
            raise HTTPUnauthorized()
        return session
