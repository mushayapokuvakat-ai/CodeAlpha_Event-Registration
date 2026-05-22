"""
URL patterns for the Registrations app.
"""

from django.urls import path
from .views import (
    RegisterForEventView,
    MyRegistrationsView,
    CancelRegistrationView,
    EventRegistrationsView,
)

urlpatterns = [
    path("register/", RegisterForEventView.as_view(), name="registration-register"),
    path("my/", MyRegistrationsView.as_view(), name="registration-my"),
    path("<int:pk>/cancel/", CancelRegistrationView.as_view(), name="registration-cancel"),
    path("event/<int:event_id>/", EventRegistrationsView.as_view(), name="registration-event-list"),
]
