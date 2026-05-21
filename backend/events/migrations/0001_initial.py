"""Events app initial migration — Event model."""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("date", models.DateTimeField()),
                ("location", models.CharField(max_length=255)),
                ("capacity", models.PositiveIntegerField()),
                ("organizer", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="events",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "events",
                "ordering": ["date"],
            },
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["date"], name="events_date_idx"),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["organizer"], name="events_organizer_idx"),
        ),
    ]
