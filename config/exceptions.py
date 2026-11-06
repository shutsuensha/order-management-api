from collections.abc import Mapping

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        request = context.get("request")
        status_code = response.status_code
        error_data = response.data
        code_by_status = {
            400: "validation_error",
            401: "authentication_error",
            403: "permission_denied",
            404: "not_found",
            405: "method_not_allowed",
            409: "conflict",
            429: "throttled",
        }

        if isinstance(error_data, Mapping) and "detail" in error_data:
            detail = str(error_data["detail"])
            fields = {
                key: value for key, value in error_data.items() if key != "detail"
            }
        elif status_code == 400:
            detail = "Request validation failed."
            fields = error_data
        else:
            detail = "Request could not be completed."
            fields = {}

        response.data = {
            "code": code_by_status.get(status_code, "api_error"),
            "detail": detail,
            "fields": fields,
            "request_id": getattr(request, "request_id", None),
        }

    return response
