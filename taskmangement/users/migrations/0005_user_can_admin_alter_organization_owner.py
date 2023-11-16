# Generated by Django 4.2.4 on 2023-10-18 05:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="can_admin",
            field=models.BooleanField(default=False, verbose_name="Can_Admin"),
        ),
        migrations.AlterField(
            model_name="organization",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="organization_admin",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
