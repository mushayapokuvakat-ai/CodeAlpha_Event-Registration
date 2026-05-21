from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "name": "Event Registration System API",
        "version": "1.0",
        "description": "A RESTful backend for managing events and registrations.",
        "endpoints": {
            "admin": "/admin/",
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "refresh_token": "/api/auth/refresh/",
                "profile": "/api/auth/me/"
            },
            "events": {
                "list_events": "/api/events/",
                "create_event": "/api/events/create/",
                "event_detail": "/api/events/<id>/",
                "update_event": "/api/events/<id>/update/",
                "delete_event": "/api/events/<id>/delete/",
                "my_events": "/api/events/my/"
            },
            "registrations": {
                "register": "/api/registrations/register/",
                "my_registrations": "/api/registrations/my/",
                "cancel_registration": "/api/registrations/<id>/cancel/",
                "event_registrations": "/api/registrations/event/<event_id>/"
            }
        }
    })

urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),

    # Auth endpoints
    path("api/auth/", include("users.urls")),

    # Event endpoints
    path("api/events/", include("events.urls")),

    # Registration endpoints
    path("api/registrations/", include("registrations.urls")),
]

