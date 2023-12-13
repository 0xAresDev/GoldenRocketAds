from django.db import models
from ServerOwner.models import AdvServerInfo, Channel
import django

# Create your models here.
class DailyIncome(models.Model):
    date = models.DateField()
    adv_server = models.ForeignKey(AdvServerInfo, on_delete=models.CASCADE, related_name="daily_incomes")
    engagement_points = models.IntegerField()
    cpm = models.FloatField()


class ChannelActivity(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="activities")
    total_messages = models.IntegerField()
    unique_messagers = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(default=django.utils.timezone.now)
    chunk = models.IntegerField()
