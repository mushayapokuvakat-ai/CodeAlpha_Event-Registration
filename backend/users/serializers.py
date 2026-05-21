"""
Serializers for the Users app.
"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from .constants import ROLE_CHOICES

User = get_user_model()


# ---------------------------------------------------------------------------
# Registration Serializer
# ---------------------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    """Handles user signup. Accepts role so organizers can self-register."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, default="USER")

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "role"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ---------------------------------------------------------------------------
# Login Serializer
# ---------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    """Validates credentials and returns the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,  # Django's authenticate uses USERNAME_FIELD
            password=password,
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        attrs["user"] = user
        return attrs


# ---------------------------------------------------------------------------
# User Info Serializer
# ---------------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a user (used in nested responses)."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "date_joined"]
        read_only_fields = fields
