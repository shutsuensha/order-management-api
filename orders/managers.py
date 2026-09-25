from django.db import models


class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status="pending")

    def expensive(self):
        return self.filter(total__gte=1000)

    def for_user(self, user):
        return self.filter(user=user)
