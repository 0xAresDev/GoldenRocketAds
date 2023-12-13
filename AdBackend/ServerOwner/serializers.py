from rest_framework import serializers
from .models import Servers, Channel
from datetime import timedelta
from django.utils import timezone

class CreateServerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Servers
        fields = ["owner", "guild"]

    def validate(self, attrs):
        guild = attrs.get("guild")
        owner = attrs.get("owner")
        if len(Servers.objects.filter(guild=guild, owner=owner)) > 0:
            return False
        elif len(Servers.objects.filter(guild=guild)) > 0:
            return False
        else:
            return attrs

    def create(self, validated_data):
        server = Servers.objects.create(guild=validated_data.get("guild"), owner=validated_data.get("owner"))
        return server


class ChannelSerializer():

    def create(self, data):
        if len(Channel.objects.filter(server=Servers.objects.get(guild=data.get("guild")).advserverinfo,
                                      channel_name=data.get("channel"))) >0:
            return False
        channel = Channel.objects.create(
            server=Servers.objects.get(guild=data.get("guild")).advserverinfo,
            channel_name=data.get("channel"),
            ad_frequency=data.get("ad_frequency"),
            ad_last_shown=(timezone.now()-timedelta(minutes=int(data.get("ad_frequency"))))
        )
        return channel

    def update(self, data):
        channel = Channel.objects.get(server=Servers.objects.get(guild=data.get("guild")).advserverinfo,
                                      channel_name=data.get("old_channel"))
        channel.channel_name = data.get("new_channel")
        channel.ad_frequency = data.get("ad_frequency")
        channel.save()
        return channel

    def delete(self, data):
        channel = Channel.objects.get(server=Servers.objects.get(guild=data.get("guild")).advserverinfo,
                                      channel_name=data.get("channel"))
        channel.delete()
        return True

