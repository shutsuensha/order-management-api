from rest_framework import serializers

from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "user", "bio"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "age", "profile", "password"]

    def validate_age(self, value: int) -> int:
        if value < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
