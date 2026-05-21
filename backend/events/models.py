"""
Event model for Event Registration System.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Event(models.Model):
    """
    Represents an event created by an organizer.

    Fields:
        name        — Event title
        description — Full description
        date        — When the event takes place (must be in the future)
        location    — Physical or virtual location
        capacity    — Maximum number of registrations allowed (must be > 0)
        organizer   — FK to the User who created this event
        created_at  — Auto-set timestamp on creation
    """

    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "events"
        ordering = ["date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["organizer"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.date.strftime('%Y-%m-%d')}"

    @property
    def available_slots(self):
        """How many registration slots remain."""
        active_count = self.registrations.filter(status="ACTIVE").count()
        return self.capacity - active_count

    @property
    def is_full(self):
        return self.available_slots <= 0
