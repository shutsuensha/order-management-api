import pytest
from django.core.cache import cache
from django.db import connection, transaction
from django.db.models import Count
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from orders.models import Order
from products.models import Category, Product
from users.models import User


@pytest.mark.django_db
def test_orders_list():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/orders/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_order():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/orders/",
        {
            "user_id": user.id,
            "number": "TEST-001",
            "total": "100.00",
            "status": "pending",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["number"] == "TEST-001"
    assert response.data["total"] == "100.00"


@pytest.mark.django_db
def test_orders_list_unauthorized():
    client = APIClient()

    response = client.get("/api/orders/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_order_detail_forbidden_for_another_user():
    user1 = User.objects.create_user(
        username="user1",
        password="12345678",
        email="user1@example.com",
        age=25,
    )

    user2 = User.objects.create_user(
        username="user2",
        password="12345678",
        email="user2@example.com",
        age=25,
    )

    order = Order.objects.create(
        user=user1,
        number="ORDER-TEST",
        total="100.00",
        status="pending",
    )

    client = APIClient()
    client.force_authenticate(user=user2)

    response = client.get(f"/api/orders/{order.id}/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_order_detail_not_found():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/orders/9999/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_order_patch():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    order = Order.objects.create(
        user=user,
        number="ORDER-PATCH",
        total="100.00",
        status="pending",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/orders/{order.id}/",
        {"status": "paid"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "paid"


@pytest.mark.django_db
def test_order_delete():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    order = Order.objects.create(
        user=user,
        number="ORDER-DELETE",
        total="100.00",
        status="pending",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/orders/{order.id}/")

    assert response.status_code == 204
    assert not Order.objects.filter(id=order.id).exists()


@pytest.mark.django_db
def test_order_put():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    order = Order.objects.create(
        user=user,
        number="ORDER-PUT",
        total="100.00",
        status="pending",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        f"/api/orders/{order.id}/",
        {
            "user_id": user.id,
            "number": "ORDER-PUT-UPDATED",
            "total": "250.00",
            "status": "paid",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["number"] == "ORDER-PUT-UPDATED"
    assert response.data["total"] == "250.00"
    assert response.data["status"] == "paid"


@pytest.mark.django_db
def test_create_order_validation_error():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/orders/",
        {
            "user_id": user.id,
            "total": "100.00",
            "status": "pending",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "number" in response.data["error"]


@pytest.mark.django_db
def test_orders_n_plus_one():
    user = User.objects.create_user(
        username="testuser",
        password="12345678",
        email="test@example.com",
        age=25,
    )

    for i in range(3):
        Order.objects.create(
            user=user,
            number=f"ORDER-{i}",
            total="100.00",
            status="pending",
        )

    orders = Order.objects.select_related("user")

    with CaptureQueriesContext(connection) as queries:
        for order in orders:
            order.user.username

    print("QUERIES:", len(queries))


@pytest.mark.django_db
def test_products_prefetch_related():
    category = Category.objects.create(name="Test")

    for i in range(3):
        product = Product.objects.create(
            name=f"Product-{i}",
            price="100.00",
        )
        product.categories.add(category)

    products = Product.objects.prefetch_related("categories")

    with CaptureQueriesContext(connection) as queries:
        for product in products:
            list(product.categories.all())

    print("QUERIES:", len(queries))


@pytest.mark.django_db
def test_product_annotate():
    category1 = Category.objects.create(name="Category 1")
    category2 = Category.objects.create(name="Category 2")

    product = Product.objects.create(
        name="Product",
        price="100.00",
    )

    product.categories.add(category1, category2)

    product = Product.objects.annotate(categories_count=Count("categories")).get(
        id=product.id
    )

    assert product.categories_count == 2


@pytest.mark.django_db
def test_transaction_rollback():
    user = User.objects.create_user(
        username="transaction-user",
        password="12345678",
        email="transaction@example.com",
        age=25,
    )

    try:
        with transaction.atomic():
            Order.objects.create(
                user=user,
                number="ROLLBACK-001",
                total="100.00",
                status="pending",
            )

            raise Exception("rollback")

    except Exception:
        pass

    assert not Order.objects.filter(number="ROLLBACK-001").exists()


@pytest.mark.django_db
def test_select_for_update():
    user = User.objects.create_user(
        username="lock-user",
        password="12345678",
        email="lock@example.com",
        age=25,
    )

    order = Order.objects.create(
        user=user,
        number="LOCK-001",
        total="100.00",
        status="pending",
    )

    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order.id)

        order.status = "paid"
        order.save()

    order.refresh_from_db()

    assert order.status == "paid"


@pytest.mark.django_db
def test_redis_cache():
    cache.set("test_key", "hello", timeout=60)

    value = cache.get("test_key")

    assert value == "hello"
