import json

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response


def json_response(data: dict | None = None, status: str = "ok") -> Response:
    if data is None:
        data = {}

    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "bad_request",
    message: str | None = None,
    data: dict | None = None,
) -> Response:
    if data is None:
        data = {}
    body = {
        "status": status,
        "message": message or "",
        "data": data,
    }
    return Response(
        status=http_status,
        body=json.dumps(body),
        content_type="application/json",
    )
