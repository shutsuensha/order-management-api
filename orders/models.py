from django.db import models

from users.models import User


class Order(models.Model):
    number = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", null=True
    )

    def __str__(self) -> str:
        return self.number
