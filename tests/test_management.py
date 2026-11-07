import pytest
from django.core.management import call_command

from categories.models import Category
from products.models import Product
from users.models import User


@pytest.mark.django_db
def test_seed_demo_command_is_idempotent():
    call_command(
        "seed_demo",
        admin_password="AdminPassword456!",
        user_password="UserPassword456!",
    )
    call_command(
        "seed_demo",
        admin_password="AdminPassword456!",
        user_password="UserPassword456!",
    )

    assert User.objects.filter(username="demo-admin", is_staff=True).count() == 1
    assert User.objects.filter(username="demo-user", is_staff=False).count() == 1
    assert Category.objects.count() == 2
    assert Product.objects.count() == 2
    assert Product.objects.get(name="Demo desk lamp").categories.count() == 2
