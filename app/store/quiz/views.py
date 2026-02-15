import json

from aiohttp.web import (HTTPBadRequest, HTTPConflict, HTTPNotFound,
                         HTTPUnauthorized)
from aiohttp_apispec import docs, request_schema, response_schema

from app.quiz.models import Answer
from app.quiz.schemes import (ListQuestionSchema, QuestionSchema,
                              ThemeListSchema, ThemeSchema)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Add new theme")
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        await self.check_auth()
        body = await self.request.read()
        raw = json.loads(body.decode()) if body else {}
        data = ThemeSchema().load(raw)
        title = data["title"]

        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            raise HTTPConflict(reason="Theme with this title already exists")

        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="List all themes")
    @response_schema(ThemeListSchema)
    async def get(self):
        await self.check_auth()
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="Add new question")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        await self.check_auth()
        body = await self.request.read()
        raw = json.loads(body.decode()) if body else {}
        data = QuestionSchema().load(raw)
        title = data["title"]
        theme_id = data["theme_id"]
        answers_data = data["answers"]

        if len(answers_data) < 2:
            raise HTTPBadRequest(
                reason="Question must have at least 2 answers")

        correct_answers = [a for a in answers_data if a["is_correct"]]
        if len(correct_answers) == 0:
            raise HTTPBadRequest(
                reason="Question must have at least one correct answer")
        if len(correct_answers) > 1:
            raise HTTPBadRequest(
                reason="Question must have exactly one correct answer")

        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            raise HTTPNotFound(reason="Theme not found")

        existing_q = await self.store.quizzes.get_question_by_title(title)
        if existing_q:
            raise HTTPConflict(reason="Question already exists")

        answers = [
            Answer(title=a["title"], is_correct=a["is_correct"])
            for a in answers_data
        ]

        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="List questions by theme")
    @response_schema(ListQuestionSchema)
    async def get(self):
        await self.check_auth()
        theme_id_str = self.request.query.get("theme_id")
        try:
            theme_id = int(theme_id_str) if theme_id_str else None
        except (TypeError, ValueError):
            theme_id = None

        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(data=ListQuestionSchema().dump({"questions":
                                                             questions}))
