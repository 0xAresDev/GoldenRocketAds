from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from .views import AdvertiserView, change_ads_on_server_view, get_ads_for_server_view
from rest_framework import status
from .models import Advertiser, Ad, Button, AdObject
from ServerOwner.models import Servers, Channel
from datetime import timedelta
from django.utils import timezone

# Create your tests here.
class AdvertiserTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        Advertiser.objects.create(company_name="X", website="url", description="ElonsGang")
        Advertiser.objects.create(company_name="T", website="url1", description="MarksGang")

    def test_get_advertisers(self):
        request = self.request_factory.get('/get-advertisers/', format='json')
        request.user = self.user
        view = AdvertiserView.as_view()
        response = view(request)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(response.data[0]["company_name"] == "X")
        self.assertTrue(response.data[1]["website"] == "url1")



class AddAndRemoveAdsFromServerTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        Advertiser.objects.create(company_name="X", website="url", description="ElonsGang")
        Advertiser.objects.create(company_name="T", website="url1", description="MarksGang")
        self.server = Servers.objects.create(owner=1, guild=1)


    def add_advertiser(self, guild, name):
        obj = {
            "guild": guild,
            "ADD": name
        }
        request = self.request_factory.patch('/change-advertisers-on-server/', obj, format='json')
        request.user = self.user
        view = change_ads_on_server_view
        response = view(request)
        return response

    def remove_advertiser(self, guild, name):
        obj = {
            "guild": guild,
            "REMOVE": name
        }
        request = self.request_factory.patch('/change-advertisers-on-server/', obj, format='json')
        request.user = self.user
        view = change_ads_on_server_view
        response = view(request)
        return response


    def test_add_advertiser_to_server(self):
        response = self.add_advertiser(1, "X")
        #print(response)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(self.server.advserverinfo.accepted_ads.all())==1)
        self.assertTrue(self.server.advserverinfo.accepted_ads.all()[0].website=="url")

    def test_remove_advertiser_to_server(self):
        response = self.add_advertiser(1, "X")
        #print(response)
        response = self.remove_advertiser(1, "X")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(self.server.advserverinfo.accepted_ads.all())==0)

class ServingAdsTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        ad1 = Advertiser.objects.create(company_name="X", website="url", description="ElonsGang")
        advert1 = Ad.objects.create(company=ad1, text="Ad Text 1")
        advert2 = Ad.objects.create(company=ad1, text="Ad Text 2")
        Ad.objects.create(company=ad1, text="Ad Text 3")
        ad1.save()
        ad2 = Advertiser.objects.create(company_name="T", website="url1", description="MarksGang")
        Ad.objects.create(company=ad2, text="Ad Text 1.1")
        Ad.objects.create(company=ad2, text="Ad Text 2.1")
        Ad.objects.create(company=ad2, text="Ad Text 3.1")
        Button.objects.create(ad=advert1, label="Ad URL", url="URL..")
        Button.objects.create(ad=advert1, label="Dude", url="URL1..")
        Button.objects.create(ad=advert2, label="32dsdsads", url="URL3..")
        ad2.save()
        self.server = Servers.objects.create(owner=1, guild=1)
        self.adv_server = self.server.advserverinfo
        self.adv_server.accepted_ads.add(ad1)
        self.adv_server.accepted_ads.add(ad2)
        self.adv_server.save()
        self.channel1 = Channel.objects.create(server=self.adv_server, channel_name="Test", ad_frequency=2, ad_last_shown=timezone.now()-timedelta(minutes=3))
        Channel.objects.create(server=self.adv_server, channel_name="Testq", ad_frequency=5,
                               ad_last_shown=timezone.now() - timedelta(minutes=6))

    def test_getting_ads(self):
        request = self.request_factory.post('/get-ads/', {"guild":1}, format='json')
        request.user = self.user
        view = get_ads_for_server_view
        response = view(request)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(response.data.keys())==2)

        self.assertTrue(Channel.objects.get(channel_name="Test").ad_last_shown+timedelta(seconds=5)>timezone.now())
        data = response.data
        ch = Channel.objects.get(channel_name=list(data.keys())[0]).pk
        self.assertTrue(AdObject.objects.get(channel_pk=ch).ad.text==data[list(data.keys())[0]]["text"])
