"""
Views for the Events app.
"""

from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .serializers import EventSerializer, EventListSerializer
from .permissions import IsOrganizer, IsEventOwnerOrAdmin


# ---------------------------------------------------------------------------
# GET /api/events/
# Public — list all upcoming events
# ---------------------------------------------------------------------------
class EventListView(generics.ListAPIView):
    """Return a paginated list of all events, ordered by date."""

    serializer_class = EventListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Event.objects.select_related("organizer").all()


# ---------------------------------------------------------------------------
# GET /api/events/{id}/
# Public — retrieve a single event with full details
# ---------------------------------------------------------------------------
class EventDetailView(generics.RetrieveAPIView):
    """Return full details of a specific event."""

    queryset = Event.objects.select_related("organizer").all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# POST /api/events/create/
# Organizer only
# ---------------------------------------------------------------------------
class EventCreateView(generics.CreateAPIView):
    """Create a new event. Only organizers can access this endpoint."""

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


# ---------------------------------------------------------------------------
# PUT/PATCH /api/events/{id}/update/
# Owner organizer or admin only
# ---------------------------------------------------------------------------
class EventUpdateView(generics.UpdateAPIView):
    """Update an event. Only the owning organizer or an admin may update."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsEventOwnerOrAdmin]


# ---------------------------------------------------------------------------
# DELETE /api/events/{id}/delete/
# Owner organizer or admin only
# ---------------------------------------------------------------------------
class EventDeleteView(generics.DestroyAPIView):
    """Delete an event. Only the owning organizer or an admin may delete."""

    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsEventOwnerOrAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Event deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# GET /api/events/my/
# Authenticated organizer — list only their own events
# ---------------------------------------------------------------------------
class MyEventsView(generics.ListAPIView):
    """Return events created by the authenticated organizer."""

    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
