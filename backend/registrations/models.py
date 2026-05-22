"""
Registration model for Event Registration System.
"""

from django.db import models
from django.conf import settings


class Registration(models.Model):
    """
    Records a user's registration for a specific event.

    Business rules enforced here:
        - `unique_together` on (event, user) prevents duplicate registrations
          at the database level — not just at the application level.
        - status field tracks ACTIVE vs CANCELLED registrations so that
          cancelled slots free up capacity for other users.
    """

    STATUS_ACTIVE = "ACTIVE"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    class Meta:
        db_table = "registrations"
        # DB-level constraint: one active+cancelled row per (event, user) pair
        unique_together = [("event", "user")]
        ordering = ["-registered_at"]
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.event.name} [{self.status}]"
