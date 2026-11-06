import logging

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def live(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


@require_GET
def ready(request: HttpRequest) -> JsonResponse:
    checks = {"database": "ok", "cache": "ok"}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        checks["database"] = "unavailable"
        logger.exception("Readiness database check failed")

    try:
        cache.set("health:ready", "ok", timeout=5)
        if cache.get("health:ready") != "ok":
            raise RuntimeError("Cache health check returned an unexpected value")
    except Exception:
        checks["cache"] = "unavailable"
        logger.exception("Readiness cache check failed")

    is_ready = all(status == "ok" for status in checks.values())
    return JsonResponse(
        {"status": "ok" if is_ready else "unavailable", "checks": checks},
        status=200 if is_ready else 503,
    )
