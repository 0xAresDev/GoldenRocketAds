from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from .views import CreateServerView, delete_server_view, channel_view
from rest_framework import status
from .models import Servers, Channel


# Create your tests here.
class ServerCreationAndDeletionTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')

    def add_server(self, owner, guild):
        obj = {
            "owner": owner,
            "guild": guild
        }
        request = self.request_factory.post('/create-server/', obj, format='json')
        request.user = self.user
        view = CreateServerView.as_view()
        response = view(request)
        return response

    def test_add_server(self):
        response = self.add_server(1,1)
        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(Servers.objects.all())==1)

    def test_delete_server(self):
        response = self.add_server(1,1)
        obj = {
            "sender": 1,
            "guild": 1
        }
        request = self.request_factory.post('/delete-server/', obj, format='json')
        request.user = self.user
        view = delete_server_view
        response = view(request)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(Servers.objects.all())==0)


class ChannelTests(TestCase):
    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        self.server = Servers.objects.create(owner=1, guild=1)

    def create_channel(self, server, name, ad_frequency):
        obj = {
            "guild": server,
            "channel": name,
            "ad_frequency": ad_frequency
        }
        request = self.request_factory.post('/channel/', obj, format='json')
        request.user = self.user
        view = channel_view
        response = view(request)
        return response

    def test_create_channel(self):
        response = self.create_channel(self.server.guild, name="ExampleChannel", ad_frequency=2)
        self.assertTrue(response.status_code==status.HTTP_201_CREATED)
        self.assertTrue(len(Channel.objects.all())==1)

    def test_change_name(self):
        response = self.create_channel(self.server.guild, name="ExampleChannel", ad_frequency=2)
        obj = {
            "guild": 1,
            "old_channel": "ExampleChannel",
            "new_channel": "NewChannel",
            "ad_frequency": 3
        }
        request = self.request_factory.put('/channel/', obj, format='json')
        request.user = self.user
        view = channel_view
        response = view(request)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(Channel.objects.all()[0].channel_name=="NewChannel")

    def test_delete_channel(self):
        response = self.create_channel(self.server.guild, name="ExampleChannel", ad_frequency=2)
        obj = {
            "guild": 1,
            "channel": "ExampleChannel",
        }
        request = self.request_factory.delete('/channel/', obj, format='json')
        request.user = self.user
        view = channel_view
        response = view(request)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(Channel.objects.all())==0)
