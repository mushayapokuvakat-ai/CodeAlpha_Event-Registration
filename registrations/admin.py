"""Registrations app admin."""
from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "registered_at")
    list_filter = ("status", "event")
    search_fields = ("user__username", "event__name")
    ordering = ("-registered_at",)
