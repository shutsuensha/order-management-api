import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .managers import OrderQuerySet


def generate_order_number() -> str:
    return f"ORD-{uuid.uuid4().hex[:20].upper()}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_order_number,
        editable=False,
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", null=True
    )

    objects = OrderQuerySet.as_manager()

    def transition_to(self, new_status: str) -> None:
        target_status = self.Status(new_status)
        allowed_transitions = {
            self.Status.PENDING: {
                self.Status.PENDING,
                self.Status.PAID,
                self.Status.CANCELED,
            },
            self.Status.PAID: {
                self.Status.PAID,
                self.Status.PROCESSING,
                self.Status.CANCELED,
            },
            self.Status.PROCESSING: {
                self.Status.PROCESSING,
                self.Status.COMPLETED,
                self.Status.CANCELED,
            },
            self.Status.COMPLETED: {self.Status.COMPLETED},
            self.Status.CANCELED: {self.Status.CANCELED},
        }

        if target_status not in allowed_transitions.get(self.status, set()):
            raise ValidationError(
                f"Order status cannot change from {self.status} to {target_status}."
            )

        self.status = target_status

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
