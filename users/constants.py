"""
Role constants for User model.
Centralised so views, serializers, and permissions all import from one place.
"""

ROLE_USER = "USER"
ROLE_ORGANIZER = "ORGANIZER"
ROLE_ADMIN = "ADMIN"

ROLE_CHOICES = [
    (ROLE_USER, "User"),
    (ROLE_ORGANIZER, "Organizer"),
    (ROLE_ADMIN, "Admin"),
]
