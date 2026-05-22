"""Registrations app initial migration — Registration model."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("events", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Registration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="registrations",
                    to="events.event",
                )),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="registrations",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("registered_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(
                    choices=[("ACTIVE", "Active"), ("CANCELLED", "Cancelled")],
                    default="ACTIVE",
                    max_length=10,
                )),
            ],
            options={
                "db_table": "registrations",
                "ordering": ["-registered_at"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="registration",
            unique_together={("event", "user")},
        ),
        migrations.AddIndex(
            model_name="registration",
            index=models.Index(fields=["event", "status"], name="reg_event_status_idx"),
        ),
        migrations.AddIndex(
            model_name="registration",
            index=models.Index(fields=["user", "status"], name="reg_user_status_idx"),
        ),
    ]
