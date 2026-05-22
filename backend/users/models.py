"""
Custom User model for Event Registration System.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from .constants import ROLE_USER, ROLE_CHOICES


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with role-based access control.

    Roles:
        USER      — can register for events
        ORGANIZER — can create and manage events
        ADMIN     — full system access
    """

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
    )

    # Required by AbstractBaseUser + PermissionsMixin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.role})"

    # ------------------------------------------------------------------
    # Role helper properties
    # ------------------------------------------------------------------
    @property
    def is_organizer(self):
        return self.role == "ORGANIZER"

    @property
    def is_admin_user(self):
        return self.role == "ADMIN"
