from django.db import models
from django.utils import timezone
import django

# Create your models here.
class Advertiser(models.Model):
    company_name = models.CharField(max_length=100)
    website = models.CharField(max_length=100)
    description = models.CharField(max_length=500)


class Ad(models.Model):
    company = models.ForeignKey(Advertiser, on_delete=models.CASCADE, related_name="ads")
    text = models.TextField()


class Button(models.Model):
    label = models.CharField(max_length=50)
    url = models.CharField(max_length=200)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name="buttons")


class AdObject(models.Model):
    channel_pk = models.IntegerField()
    server_id = models.IntegerField()
    time = models.DateTimeField(default=django.utils.timezone.now)
    ad = models.ForeignKey(Ad, on_delete=models.DO_NOTHING, related_name="live_instances")

