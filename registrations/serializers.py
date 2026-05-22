"""
Serializers for the Registrations app.
"""

from django.db import transaction
from rest_framework import serializers

from .models import Registration
from events.models import Event
from events.serializers import EventListSerializer
from users.serializers import UserSerializer


# ---------------------------------------------------------------------------
# Register for Event Serializer
# ---------------------------------------------------------------------------
class RegisterForEventSerializer(serializers.Serializer):
    """
    Accepts an event_id and performs all business-rule checks before saving.

    Checks (in order):
        1. Event exists
        2. Event has available capacity
        3. User has not already registered (ACTIVE)
    """

    event_id = serializers.IntegerField()

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(pk=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
        self._event = event
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        event = self._event

        # Check for existing ACTIVE registration
        if Registration.objects.filter(event=event, user=user, status="ACTIVE").exists():
            raise serializers.ValidationError({"error": "User already registered for this event."})

        # Check capacity using select_for_update to prevent race conditions
        with transaction.atomic():
            active_count = (
                Registration.objects
                .select_for_update()
                .filter(event=event, status="ACTIVE")
                .count()
            )
            if active_count >= event.capacity:
                raise serializers.ValidationError({"error": "Event capacity reached."})

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        event = self._event

        # If user previously cancelled, reactivate instead of creating duplicate
        registration, created = Registration.objects.get_or_create(
            event=event,
            user=user,
            defaults={"status": "ACTIVE"},
        )
        if not created and registration.status == "CANCELLED":
            # Re-check capacity before reactivating
            active_count = Registration.objects.filter(event=event, status="ACTIVE").count()
            if active_count >= event.capacity:
                raise serializers.ValidationError({"error": "Event capacity reached."})
            registration.status = "ACTIVE"
            registration.save()

        return registration


# ---------------------------------------------------------------------------
# Registration Detail Serializer (for list & response)
# ---------------------------------------------------------------------------
class RegistrationSerializer(serializers.ModelSerializer):
    """Full representation of a registration, including nested event and user."""

    event = EventListSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "event", "user", "registered_at", "status"]
        read_only_fields = fields
