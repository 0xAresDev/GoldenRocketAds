# Generated by Django 4.2.6 on 2023-10-26 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Ads", "0002_button"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ad",
            name="text",
            field=models.TextField(),
        ),
    ]
