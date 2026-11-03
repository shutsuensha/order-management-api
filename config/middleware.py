import logging
import time

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("config.request")


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()

        response = self.get_response(request)

        duration = time.perf_counter() - start

        logger.info(
            "%s %s -> %s in %.4fs",
            request.method,
            request.path,
            response.status_code,
            duration,
        )

        return response
