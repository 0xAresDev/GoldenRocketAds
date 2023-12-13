# Generated by Django 4.2.6 on 2023-10-29 16:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("ServerOwner", "0002_advserverinfo_current_cpm"),
        ("RevenueGen", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dailyincome",
            old_name="amount",
            new_name="cpm",
        ),
        migrations.AddField(
            model_name="dailyincome",
            name="engagement_points",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="ChannelActivity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_messages", models.IntegerField()),
                ("unique_messagers", models.IntegerField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("chunk", models.IntegerField()),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="ServerOwner.channel",
                    ),
                ),
            ],
        ),
    ]
