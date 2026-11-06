from decimal import Decimal
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from products.models import Product
from users.models import User


@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        identifier = uuid4().hex[:10]
        data = {
            "username": f"test-user-{identifier}",
            "email": f"test-{identifier}@example.com",
            "password": "StrongPassword123!",
            "age": 25,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    return create_user


@pytest.fixture
def product_factory(db):
    def create_product(**kwargs):
        identifier = uuid4().hex[:10]
        data = {
            "name": f"Test product {identifier}",
            "price": Decimal("10.00"),
            "stock": 10,
        }
        data.update(kwargs)
        return Product.objects.create(**data)

    return create_product


@pytest.fixture
def order_factory(db, user_factory):
    def create_order(**kwargs):
        data = {
            "user": user_factory(),
            "total": Decimal("10.00"),
            "status": Order.Status.PENDING,
        }
        data.update(kwargs)
        return Order.objects.create(**data)

    return create_order


@pytest.fixture
def order_item_factory(db, product_factory):
    def create_order_item(order, **kwargs):
        product = kwargs.pop("product", None) or product_factory()
        data = {
            "order": order,
            "product": product,
            "quantity": 1,
            "product_name": product.name,
            "unit_price": product.price,
        }
        data.update(kwargs)
        return OrderItem.objects.create(**data)

    return create_order_item


@pytest.fixture
def authenticated_client():
    def create_client(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    return create_client
