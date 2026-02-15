import hashlib
import typing

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class AdminAccessor(BaseAccessor):
    @property
    def _db(self):
        return self.app.store.database

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self._db.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(
            id=self._db.next_admin_id,
            email=email,
            password=_hash_password(password),
        )
        self._db.admins.append(admin)
        return admin

    async def connect(self, app: "Application"):
        if not self._db.admins and hasattr(app, "config") and app.config:
            await self.create_admin(
                email=app.config.admin.email,
                password=app.config.admin.password,
            )
