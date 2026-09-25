import time

from django.http import HttpRequest, HttpResponse


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()

        response = self.get_response(request)

        duration = time.perf_counter() - start

        print(f"{request.method} {request.path} - {duration:.4f}s")

        return response


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("DEBUG: before")

        response = self.get_response(request)

        print("DEBUG: after")

        return response
