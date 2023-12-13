from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from Ads.models import Advertiser


# Create your models here.
class Servers(models.Model):
    owner = models.IntegerField()
    guild = models.IntegerField(primary_key=True)

class AdvServerInfo(models.Model):
    server = models.OneToOneField(Servers, on_delete=models.CASCADE)
    accepted_ads = models.ManyToManyField(Advertiser)
    current_cpm = models.FloatField(default=0)

class Channel(models.Model):
    server = models.ForeignKey(AdvServerInfo, on_delete=models.CASCADE, related_name="channels")
    channel_name = models.CharField(max_length=100)
    ad_frequency = models.IntegerField()
    ad_last_shown = models.DateTimeField()


@receiver(post_save, sender=Servers)
def create_adv_server(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user profile object is created."""
    if created:
        AdvServerInfo.objects.create(server=instance)
