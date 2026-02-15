import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig | None = None
    bot: BotConfig | None = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    admin_cfg = raw_config.get("admin", {})
    session_cfg = raw_config.get("session")
    bot_cfg = raw_config.get("bot")

    app.config = Config(
        admin=AdminConfig(
            email=admin_cfg["email"],
            password=admin_cfg["password"],
        ),
        session=(
            SessionConfig(key=session_cfg["key"])
            if session_cfg and "key" in session_cfg
            else None
        ),
        bot=(
            BotConfig(
                token=bot_cfg["token"],
                group_id=bot_cfg["group_id"],
            )
            if bot_cfg and "token" in bot_cfg and "group_id" in bot_cfg
            else None
        ),
    )
