"""
Views for the Registrations app.
"""

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from .models import Registration
from .serializers import RegisterForEventSerializer, RegistrationSerializer
from events.permissions import IsOrganizer, IsAdminUser


# ---------------------------------------------------------------------------
# POST /api/registrations/register/
# Authenticated users only
# ---------------------------------------------------------------------------
class RegisterForEventView(APIView):
    """
    Register the authenticated user for an event.

    Business rules enforced by RegisterForEventSerializer:
        - Event must exist
        - Event must have available capacity
        - User must not already be actively registered
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterForEventSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            with transaction.atomic():
                registration = serializer.save()
            return Response(
                {
                    "message": "Registration successful.",
                    "registration_id": registration.id,
                    "event": registration.event.name,
                    "status": registration.status,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# GET /api/registrations/my/
# Authenticated users — own registrations only
# ---------------------------------------------------------------------------
class MyRegistrationsView(generics.ListAPIView):
    """
    List all registrations (both ACTIVE and CANCELLED) for the
    currently authenticated user.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Registration.objects
            .filter(user=self.request.user)
            .select_related("event", "event__organizer", "user")
        )


# ---------------------------------------------------------------------------
# DELETE /api/registrations/{id}/cancel/
# Owner of the registration only
# ---------------------------------------------------------------------------
class CancelRegistrationView(APIView):
    """
    Cancel a registration by setting status to CANCELLED.

    Rules:
        - Only the registration owner can cancel their own registration.
        - Organizers and admins can view all registrations but cannot cancel
          another user's registration through this endpoint.
        - Returns 404 if the registration does not belong to the user.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            registration = Registration.objects.get(pk=pk, user=request.user)
        except Registration.DoesNotExist:
            return Response(
                {"error": "Registration not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if registration.status == "CANCELLED":
            return Response(
                {"error": "This registration is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration.status = "CANCELLED"
        registration.save()

        return Response(
            {
                "message": "Registration cancelled successfully.",
                "registration_id": registration.id,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# GET /api/registrations/event/{event_id}/
# Organizer (own events) or Admin — all registrations for a given event
# ---------------------------------------------------------------------------
class EventRegistrationsView(generics.ListAPIView):
    """
    List all registrations for a specific event.
    Accessible by the event's organizer or any admin.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        user = self.request.user

        qs = (
            Registration.objects
            .filter(event_id=event_id)
            .select_related("event", "user")
        )

        # Admins see everything; organizers only see their own events
        if user.role == "ADMIN":
            return qs
        if user.role == "ORGANIZER":
            return qs.filter(event__organizer=user)

        # Regular users are not allowed
        return Registration.objects.none()

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.role not in ("ADMIN", "ORGANIZER"):
            return Response(
                {"error": "You do not have permission to view event registrations."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)
