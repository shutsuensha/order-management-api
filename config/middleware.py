import logging
import time
import uuid

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("config.request")


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.request_id = uuid.uuid4().hex
        start = time.perf_counter()

        response = self.get_response(request)

        duration = time.perf_counter() - start

        logger.info(
            "%s %s -> %s in %.4fs request_id=%s",
            request.method,
            request.path,
            response.status_code,
            duration,
            request.request_id,
        )
        response["X-Request-ID"] = request.request_id

        return response
