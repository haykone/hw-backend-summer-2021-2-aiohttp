import hashlib

from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class AdminLoginView(View):
    async def post(self):
        data = await self.request.json()
        schema = AdminSchema()
        clean_data = schema.load(data)

        email = clean_data["email"]
        password = clean_data["password"]

        admin = await self.store.database.get_admin_by_email(email)
        if not admin or admin.password != _hash_password(password):
            raise HTTPForbidden(reason="Invalid email or password")

        admin_data = {"id": admin.id, "email": admin.email}

        session = await new_session(self.request)
        session["admin"] = admin_data

        return json_response(data=admin_data)


class AdminCurrentView(AuthRequiredMixin, View):
    async def get(self):
        session = await self.check_auth()
        return json_response(data=session["admin"])
