from django.core.management.base import BaseCommand

from categories.models import Category
from products.models import Product
from users.models import User


class Command(BaseCommand):
    help = "Create or update demo users, categories, and products."

    def add_arguments(self, parser):
        parser.add_argument("--admin-password", default="AdminDemo123!")
        parser.add_argument("--user-password", default="UserDemo123!")

    def handle(self, *args, **options):
        admin = self._upsert_user(
            username="demo-admin",
            email="demo-admin@example.com",
            password=options["admin_password"],
            is_staff=True,
            is_superuser=True,
        )
        user = self._upsert_user(
            username="demo-user",
            email="demo-user@example.com",
            password=options["user_password"],
            is_staff=False,
            is_superuser=False,
        )

        electronics = self._upsert_category("Electronics", "Devices and accessories")
        home = self._upsert_category("Home", "Useful products for home")

        self._upsert_product(
            "Demo keyboard",
            "49.90",
            25,
            "Mechanical keyboard for the demo catalog.",
            [electronics],
        )
        self._upsert_product(
            "Demo desk lamp",
            "29.90",
            15,
            "Desk lamp for the demo catalog.",
            [home, electronics],
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data ready: "
                f"admin={admin.username}, user={user.username}, "
                "categories=2, products=2"
            )
        )

    @staticmethod
    def _upsert_user(*, username, email, password, is_staff, is_superuser):
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "email": email,
                "age": 25,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
                "is_active": True,
            },
        )
        user.set_password(password)
        user.save(update_fields=["password"])
        return user

    @staticmethod
    def _upsert_category(name, description):
        category, _ = Category.objects.update_or_create(
            name=name,
            defaults={"description": description},
        )
        return category

    @staticmethod
    def _upsert_product(name, price, stock, description, categories):
        product, _ = Product.objects.update_or_create(
            name=name,
            defaults={
                "price": price,
                "stock": stock,
                "description": description,
            },
        )
        product.categories.set(categories)
        return product
