from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "user", "bio"]
        read_only_fields = ["id", "user"]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "age", "password"]
        read_only_fields = ["id"]

    def validate_age(self, value: int) -> int:
        if value < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "age"]
        read_only_fields = fields


class AdminUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "age",
            "profile",
            "is_staff",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def validate_age(self, value: int) -> int:
        if value < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        return value


class MeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "bio"]
        read_only_fields = ["id"]


class MeSerializer(serializers.ModelSerializer):
    profile = MeProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "age", "profile"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data is not None:
            Profile.objects.update_or_create(
                user=instance,
                defaults=profile_data,
            )

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value, user=self.context["request"].user)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
