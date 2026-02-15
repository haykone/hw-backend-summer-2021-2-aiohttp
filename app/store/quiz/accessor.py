from app.base.base_accessor import BaseAccessor
from app.quiz.models import Answer, Question, Theme


class QuizAccessor(BaseAccessor):
    @property
    def _db(self):
        return self.app.store.database

    async def create_theme(self, title: str) -> Theme:
        theme = Theme(id=self._db.next_theme_id, title=title)
        self._db.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Theme | None:
        for theme in self._db.themes:
            if theme.title == title:
                return theme
        return None

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        for theme in self._db.themes:
            if theme.id == id_:
                return theme
        return None

    async def list_themes(self) -> list[Theme]:
        return self._db.themes.copy()

    async def get_question_by_title(self, title: str) -> Question | None:
        for question in self._db.questions:
            if question.title == title:
                return question
        return None

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        question = Question(
            id=self._db.next_question_id,
            title=title,
            theme_id=theme_id,
            answers=answers
        )
        self._db.questions.append(question)
        return question

    async def list_questions(
        self, theme_id: int | None = None
    ) -> list[Question]:
        if theme_id is not None:
            return [q for q in self._db.questions if q.theme_id == theme_id]
        return self._db.questions.copy()
