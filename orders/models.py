from django.db import models


class Order(models.Model):
    number = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.number
