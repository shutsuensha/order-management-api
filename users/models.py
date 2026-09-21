from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.username
