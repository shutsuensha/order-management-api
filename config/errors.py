from rest_framework.response import Response


def conflict_response(request, code: str, detail: str) -> Response:
    return Response(
        {
            "code": code,
            "detail": detail,
            "fields": {},
            "request_id": getattr(request, "request_id", None),
        },
        status=409,
    )
