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
