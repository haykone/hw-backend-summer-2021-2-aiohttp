from dataclasses import dataclass, field
from typing import List, Optional

from app.admin.models import Admin
from app.quiz.models import Question, Theme


@dataclass
class Database:
    themes: list[Theme] = field(default_factory=list)
    admins: list[Admin] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)

    @property
    def next_theme_id(self) -> int:
        return len(self.themes) + 1

    @property
    def next_admin_id(self) -> int:
        return len(self.admins) + 1

    @property
    def next_question_id(self) -> int:
        return len(self.questions) + 1

    def clear(self):
        self.themes.clear()
        self.admins.clear()
        self.questions.clear()

    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        for admin in self.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(
            id=self.next_admin_id,
            email=email,
            password=password
        )
        self.admins.append(admin)
        return admin

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        for theme in self.themes:
            if theme.title == title:
                return theme
        return None

    async def create_theme(self, title: str) -> Theme:
        theme = Theme(
            id=self.next_theme_id,
            title=title
        )
        self.themes.append(theme)
        return theme

    async def get_all_themes(self) -> List[Theme]:
        return self.themes.copy()
