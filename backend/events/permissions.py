"""
Custom DRF permissions for the Events app.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizer(BasePermission):
    """Allow access only to users with ORGANIZER role."""

    message = "Only organizers are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ORGANIZER"
        )


class IsAdminUser(BasePermission):
    """Allow access only to users with ADMIN role."""

    message = "Only admins are allowed to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsEventOwnerOrAdmin(BasePermission):
    """
    Object-level permission:
    - ORGANIZER can update/delete only their own events
    - ADMIN can update/delete any event
    """

    message = "You do not have permission to modify this event."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "ADMIN":
            return True
        return obj.organizer == request.user
