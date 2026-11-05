import pytest
from rest_framework.test import APIClient

from categories.models import Category
from products.models import Product


@pytest.mark.django_db
def test_catalog_read_is_public():
    category = Category.objects.create(name="Public category")
    Product.objects.create(
        name="Public product",
        price="10.00",
        stock=3,
    ).categories.add(category)

    client = APIClient()

    category_response = client.get("/api/v1/categories/")
    product_response = client.get("/api/v1/products/")

    assert category_response.status_code == 200
    assert product_response.status_code == 200


@pytest.mark.django_db
def test_catalog_mutations_require_admin():
    client = APIClient()

    category_response = client.post(
        "/api/v1/categories/",
        {"name": "Protected category"},
        format="json",
    )
    product_response = client.post(
        "/api/v1/products/",
        {"name": "Protected product", "price": "10.00", "stock": 1},
        format="json",
    )

    assert category_response.status_code in {401, 403}
    assert product_response.status_code in {401, 403}
