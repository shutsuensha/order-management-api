from django.db import models

from categories.models import Category


class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    categories = models.ManyToManyField(
        Category,
        related_name="products",
        blank=True,
    )

    def __str__(self) -> str:
        return self.name
