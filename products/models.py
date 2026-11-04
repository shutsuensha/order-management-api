from django.db import models

from categories.models import Category


class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    categories = models.ManyToManyField(
        Category,
        related_name="products",
        blank=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name="product_stock_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        return self.name
