from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_id",
            "number",
            "total",
            "status",
        ]
