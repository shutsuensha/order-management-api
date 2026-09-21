from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "age"]

    def validate_age(self, value: int) -> int:
        if value < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        return value
