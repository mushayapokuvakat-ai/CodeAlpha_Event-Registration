"""
Custom User Manager for the Event Registration System.
"""

from django.contrib.auth.models import BaseUserManager
from .constants import ROLE_USER, ROLE_ADMIN


class UserManager(BaseUserManager):
    """Manager for custom User model using email as the unique identifier."""

    def create_user(self, email, username, password=None, role=ROLE_USER, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        if not username:
            raise ValueError("Username is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, role=ROLE_ADMIN, **extra_fields)
