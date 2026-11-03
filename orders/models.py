from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .managers import OrderQuerySet


class Order(models.Model):
    number = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, db_index=True)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", null=True
    )

    objects = OrderQuerySet.as_manager()

    def __str__(self) -> str:
        return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    product_name = models.CharField(max_length=150)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="order_item_quantity_gte_one",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="order_item_unit_price_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"
