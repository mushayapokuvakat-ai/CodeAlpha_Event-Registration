"""
Serializers for the Events app.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import Event
from users.serializers import UserSerializer


class EventSerializer(serializers.ModelSerializer):
    """
    Full Event serializer used for list, detail, create, and update.

    - `organizer` is auto-set from request.user on create.
    - `available_slots` and `is_full` are computed read-only fields.
    """

    organizer = UserSerializer(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "date",
            "location",
            "capacity",
            "organizer",
            "available_slots",
            "is_full",
            "created_at",
        ]
        read_only_fields = ["id", "organizer", "available_slots", "is_full", "created_at"]

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_date(self, value):
        """Event date must be in the future."""
        if value <= timezone.now():
            raise serializers.ValidationError("Event date must be a future date.")
        return value

    def validate_capacity(self, value):
        """Capacity must be a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        return value

    # ------------------------------------------------------------------
    # Create — attach organizer from request context
    # ------------------------------------------------------------------
    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["organizer"] = request.user
        return super().create(validated_data)


class EventListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views — omits full organizer details.
    """

    organizer_name = serializers.CharField(source="organizer.username", read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "date",
            "location",
            "capacity",
            "available_slots",
            "is_full",
            "organizer_name",
        ]
