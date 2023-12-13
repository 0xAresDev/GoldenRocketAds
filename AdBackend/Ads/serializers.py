from rest_framework import serializers
from .models import Advertiser, Ad, Button, AdObject
from ServerOwner.models import AdvServerInfo, Servers
from datetime import timedelta
from django.utils import timezone
import random

class AdvertiserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertiser
        fields = ["company_name", "website", "description"]

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ["text",]

class AdvertisersToServerSerializer():

    def add(self, guild, company_name):
        adv_server = Servers.objects.get(guild=guild).advserverinfo
        advertiser = Advertiser.objects.get(company_name=company_name)
        adv_server.accepted_ads.add(advertiser)
        adv_server.save()
        return adv_server

    def remove(self, guild, company_name):
        adv_server = Servers.objects.get(guild=guild).advserverinfo
        advertiser = Advertiser.objects.get(company_name=company_name)
        adv_server.accepted_ads.remove(advertiser)
        adv_server.save()
        return adv_server

class AdObjectSerializer:

    def create(self, ad, server, channel):
        AdObject.objects.create(ad=ad, server_id=server, channel_pk=channel)

class ServeAdsSerializer():

    ad_object_seri = AdObjectSerializer()
    def get_ads(self, guild):
        now = timezone.now()
        ads = {}
        adv_server = Servers.objects.get(guild=guild).advserverinfo
        advertisers = adv_server.accepted_ads.all()
        #print(advertisers)
        if len(advertisers)>0:
            channels = adv_server.channels.all()
            for channel in channels:
                if channel.ad_last_shown < now-timedelta(minutes=channel.ad_frequency):
                    advertiser = random.choice(advertisers)
                    adv_ads = advertiser.ads.all()
                    ad = random.choice(adv_ads)
                    self.ad_object_seri.create(ad=ad, server=guild, channel=channel.pk)
                    buttons = Button.objects.filter(ad=ad)
                    button_list = []
                    for b in buttons:
                        button_list.append({"label":b.label, "url":b.url})
                    ads[channel.channel_name] = {"text": ad.text, "buttons": button_list}
                    channel.ad_last_shown = now
                    channel.save()
            #return ads
            return ads
        else:
            return False


