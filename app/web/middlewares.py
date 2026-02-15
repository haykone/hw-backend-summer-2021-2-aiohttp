import json

from aiohttp import web
from aiohttp.web_exceptions import HTTPException
from marshmallow import ValidationError as MarshmallowValidationError

from app.web.utils import error_json_response


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except json.JSONDecodeError as e:
        return error_json_response(
            http_status=400,
            status="bad_request",
            message="Invalid JSON",
            data={},
        )
    except MarshmallowValidationError as e:
        return error_json_response(
            http_status=400,
            status="bad_request",
            message="Unprocessable Entity",
            data={"json": e.messages},
        )
    except HTTPException as e:
        status_map = {
            400: "bad_request",
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            409: "conflict",
        }
        return error_json_response(
            http_status=e.status,
            status=status_map.get(e.status, "error"),
            message=e.reason or "",
            data={},
        )
    except Exception as e:
        return error_json_response(
            http_status=500,
            status="internal_error",
            message=str(e),
            data={},
        )


def setup_middlewares(app):
    app.middlewares.append(error_middleware)
