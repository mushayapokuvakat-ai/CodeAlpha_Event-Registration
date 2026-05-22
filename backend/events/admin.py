"""Events app admin."""
from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "capacity", "organizer", "created_at")
    list_filter = ("date", "organizer")
    search_fields = ("name", "location", "organizer__username")
    ordering = ("date",)
