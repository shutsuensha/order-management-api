import pytest
from rest_framework.test import APIClient


def test_error_response_has_standard_envelope():
    response = APIClient().get("/api/v1/orders/")

    assert response.status_code == 401
    assert set(response.data) == {"code", "detail", "fields", "request_id"}
    assert response.data["code"] == "authentication_error"


def test_responses_include_request_id_header_and_request_log(caplog):
    caplog.set_level("INFO", logger="config.request")
    response = APIClient().get("/health/live")

    request_id = response.headers.get("X-Request-ID")
    assert response.status_code == 200
    assert request_id is not None
    assert len(request_id) == 32
    assert any(request_id in record.getMessage() for record in caplog.records)


@pytest.mark.django_db
def test_order_list_supports_pagination_filter_search_and_ordering(
    user_factory, order_factory, authenticated_client
):
    user = user_factory()
    order_factory(user=user, number="ORD-LOW", total="10.00", status="pending")
    order_factory(user=user, number="ORD-HIGH", total="20.00", status="paid")
    order_factory(user=user, number="OTHER", total="30.00", status="pending")
    client = authenticated_client(user)

    response = client.get(
        "/api/v1/orders/?page_size=1&status=pending&search=ORD&ordering=-total"
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["number"] == "ORD-LOW"


def test_openapi_schema_documents_order_contract():
    response = APIClient().get("/api/v1/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    schema = response.json()
    order_list = schema["paths"]["/api/v1/orders/"]["get"]
    order_cancel = schema["paths"]["/api/v1/orders/{id}/cancel/"]["post"]
    parameter_names = {parameter["name"] for parameter in order_list["parameters"]}

    assert {"page", "page_size", "status", "search", "ordering"} <= parameter_names
    assert order_cancel["operationId"] == "orders_cancel"
