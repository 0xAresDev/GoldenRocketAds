from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from .views import add_server_activity, get_activity_points, get_all_engagement_points_in_time_period_view, get_daily_incomes_view
from rest_framework import status
from .models import DailyIncome, ChannelActivity
from ServerOwner.models import Servers, Channel, AdvServerInfo
from datetime import timedelta, datetime, time
from django.utils import timezone
from datetime import date
from Ads.models import Advertiser, Ad, Button, AdObject
import random
from .serializers import CalculateDailyIncomeSerializer, DailyIncomeSerializer

"""# Create your tests here.
class AdvertiserTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        self.server = Servers.objects.create(owner=1, guild=1)
        self.adv_server = self.server.advserverinfo
        DailyIncome.objects.create(date=date.today(), adv_server=self.adv_server, amount=10.32)
        DailyIncome.objects.create(date=date.today()-timedelta(days=1), adv_server=self.adv_server, amount=15.32)
        DailyIncome.objects.create(date=date.today() - timedelta(days=1), adv_server=self.adv_server, amount=2.32)

    def test_get_all_ads(self):
        obj = {"guild":1}
        request = self.request_factory.post('get-income/', obj, format='json')
        request.user = self.user
        #print(request.data)
        view = get_all_daily_incomes_view
        response = view(request)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(response.data[0]["amount"]==10.32)
        self.assertTrue(response.data[2]["amount"] == 2.32)
"""

class ChannelActivityTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        self.server = Servers.objects.create(owner=1, guild=1)
        self.adv_server = self.server.advserverinfo
        self.adv_server.save()
        self.channel1 = Channel.objects.create(server=self.adv_server, channel_name="Test", ad_frequency=2, ad_last_shown=timezone.now()-timedelta(minutes=3))
        self.channel2 = Channel.objects.create(server=self.adv_server, channel_name="Testq", ad_frequency=5,
                               ad_last_shown=timezone.now() - timedelta(minutes=6))

    def add_activity(self, unique_m, total_m, start_time, guild, channel_name):
        obj = {
            "unique_messages": unique_m,
            "total_messages": total_m,
            "start_time": start_time.isoformat(),
            "guild": guild,
            "channel_name": channel_name
        }
        request = self.request_factory.post('/add-activity/', obj, format='json')
        request.user = self.user
        view = add_server_activity
        response = view(request)
        return response

    def test_adding_activity(self):
        response = self.add_activity(10, 20, start_time=timezone.now()-timedelta(minutes=6), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(ChannelActivity.objects.all())==1)
        act = ChannelActivity.objects.all()[0]
        self.assertTrue(act.channel == self.channel1)
        self.assertTrue(act.unique_messagers == 10)


    def test_adding_multiple_activities(self):
        response = self.add_activity(10, 20, start_time=timezone.now()-timedelta(minutes=25), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(30, 40, start_time=timezone.now() - timedelta(minutes=20), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(30, 40, start_time=timezone.now() - timedelta(minutes=19), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(5, 10, start_time=timezone.now() - timedelta(minutes=5), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(ChannelActivity.objects.all())==4)


class ActivityPointsTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        self.server = Servers.objects.create(owner=1, guild=1)
        self.adv_server = self.server.advserverinfo
        self.ad1 = Advertiser.objects.create(company_name="X", website="url", description="ElonsGang")
        self.advert1 = Ad.objects.create(company=self.ad1, text="Ad Text 1")
        self.adv_server.accepted_ads.add(self.ad1)
        self.adv_server.save()
        self.channel1 = Channel.objects.create(server=self.adv_server, channel_name="Test", ad_frequency=120, ad_last_shown=timezone.now()-timedelta(minutes=3))
        self.channel2 = Channel.objects.create(server=self.adv_server, channel_name="Testq", ad_frequency=20,
                               ad_last_shown=timezone.now() - timedelta(minutes=6))
        self.adobject = AdObject.objects.create(channel_pk=self.channel1.pk, server_id=self.server.guild, ad=self.advert1)
        self.adobject2 = AdObject.objects.create(channel_pk=self.channel2.pk, server_id=self.server.guild,
                                                ad=self.advert1)
        #print("Init " + str(timezone.now()-timedelta(minutes=60)))

    def add_activity(self, unique_m, total_m, start_time, guild, channel_name, end_time=None):
        obj = {
            "unique_messages": unique_m,
            "total_messages": total_m,
            "start_time": start_time.isoformat(),
            "guild": guild,
            "channel_name": channel_name
        }
        if end_time:
            obj["end_time"] = end_time.isoformat()
        request = self.request_factory.post('/add-activity/', obj, format='json')
        request.user = self.user
        view = add_server_activity
        response = view(request)
        return response

    def activity_simulation(self):
        for i in range(10):
           AdObject.objects.create(channel_pk=self.channel1.pk, server_id=self.server.guild, ad=self.advert1, time=timezone.now()-timedelta(minutes=random.randint(0,255)))

        for i in range(10):
           AdObject.objects.create(channel_pk=self.channel1.pk, server_id=self.server.guild, ad=self.advert1, time=timezone.now()+timedelta(minutes=random.randint(0,255)))

        for i in range(50):
            total = random.randint(0,100)
            unique = random.randint(0, total)
            self.add_activity(unique, total, start_time=timezone.now() - timedelta(minutes=random.randint(0, 1000)), guild=self.server.guild,
                              channel_name=self.channel1.channel_name)
        for i in range(50):
            total = random.randint(0, 100)
            unique = random.randint(0, total)
            self.add_activity(unique, total, start_time=timezone.now() + timedelta(minutes=random.randint(0, 1000)), guild=self.server.guild,
                              channel_name=self.channel1.channel_name)

    def test_get_activity(self):
        #print(timezone.now()-timedelta(minutes=60))
        #print(timezone.now()-timedelta(minutes=75))
        response = self.add_activity(10, 20, start_time=timezone.now()-timedelta(minutes=15), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(10, 20, start_time=timezone.now() - timedelta(minutes=10), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(10, 20, start_time=timezone.now() - timedelta(minutes=5), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(10, 20, start_time=timezone.now() - timedelta(minutes=0), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(10, 20, start_time=timezone.now() + timedelta(minutes=10), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(10, 20, start_time=timezone.now() + timedelta(minutes=15), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)
        response = self.add_activity(10, 20, start_time=timezone.now() + timedelta(minutes=20), guild=self.server.guild,
                                     channel_name=self.channel1.channel_name)

        request = self.request_factory.post('/get-ad-engagement/', {"pk": self.adobject.pk}, format='json')
        request.user = self.user
        view = get_activity_points
        response = view(request)
        #print(response.data)
        """print("AdObject: " + str(self.adobject.time))
        for obj in ChannelActivity.objects.all():
            print(obj.start_time)"""
        self.assertTrue(response.status_code == status.HTTP_200_OK)


    def test_get_engagement_in_timeperiod(self):
        self.activity_simulation()
        request = self.request_factory.post('/get-engagement-points-in-time-period/',
                                            {"guild": self.server.guild, "start":(timezone.now()-timedelta(minutes=500)).isoformat(), "end":(timezone.now()+timedelta(minutes=500)).isoformat()},
                                            format='json')
        request.user = self.user
        view = get_all_engagement_points_in_time_period_view
        response = view(request)
        # print(response.data)
        """print("AdObject: " + str(self.adobject.time))
        for obj in ChannelActivity.objects.all():
            print(obj.start_time)"""
        #print(response.data)
        self.assertTrue(response.status_code == status.HTTP_200_OK)


    def test_algorithm_accuracy_slow_channel(self):
        response = self.add_activity(5, 20, start_time=timezone.now() - timedelta(minutes=9), end_time=timezone.now() - timedelta(minutes=4), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(2, 3, start_time=timezone.now() - timedelta(minutes=4),  end_time=timezone.now() + timedelta(minutes=1), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(13, 33, start_time=timezone.now() + timedelta(minutes=2),  end_time=timezone.now() + timedelta(minutes=8), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(7, 14, start_time=timezone.now() + timedelta(minutes=7),  end_time=timezone.now() + timedelta(minutes=12), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        request = self.request_factory.post('/get-ad-engagement/', {"pk": self.adobject2.pk}, format='json')
        request.user = self.user
        view = get_activity_points
        response = view(request)
        self.assertTrue(response.data["points"]==40.5)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

    def test_algorithm_accuracy_slow_channel_with_outside_act(self):
        response = self.add_activity(8, 25, start_time=timezone.now() - timedelta(minutes=14),
                                     end_time=timezone.now() - timedelta(minutes=4), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(5, 20, start_time=timezone.now() - timedelta(minutes=9), end_time=timezone.now() - timedelta(minutes=4), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(2, 3, start_time=timezone.now() - timedelta(minutes=4),  end_time=timezone.now() + timedelta(minutes=1), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(13, 33, start_time=timezone.now() + timedelta(minutes=2),  end_time=timezone.now() + timedelta(minutes=8), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(7, 14, start_time=timezone.now() + timedelta(minutes=7),  end_time=timezone.now() + timedelta(minutes=12), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(7, 14, start_time=timezone.now() + timedelta(minutes=12),
                                     end_time=timezone.now() + timedelta(minutes=12), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        request = self.request_factory.post('/get-ad-engagement/', {"pk": self.adobject2.pk}, format='json')
        request.user = self.user
        view = get_activity_points
        response = view(request)
        self.assertTrue(response.data["points"]==40.5)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

    def test_algorithm_accuracy_fast_channel(self):
        response = self.add_activity(84, 101, start_time=timezone.now() - timedelta(minutes=9), end_time=timezone.now() - timedelta(minutes=4), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(68, 121, start_time=timezone.now() - timedelta(minutes=4),  end_time=timezone.now() + timedelta(minutes=1), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(34, 81, start_time=timezone.now() + timedelta(minutes=2),  end_time=timezone.now() + timedelta(minutes=8), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(61, 151, start_time=timezone.now() + timedelta(minutes=7),  end_time=timezone.now() + timedelta(minutes=12), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        request = self.request_factory.post('/get-ad-engagement/', {"pk": self.adobject2.pk}, format='json')
        request.user = self.user
        view = get_activity_points
        response = view(request)
        self.assertTrue(response.data["points"]==306)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

    def test_algorithm_accuracy_fast_channel_missing_data(self):
        response = self.add_activity(84, 101, start_time=timezone.now() - timedelta(minutes=9), end_time=timezone.now() - timedelta(minutes=4), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        response = self.add_activity(68, 121, start_time=timezone.now() - timedelta(minutes=4),  end_time=timezone.now() + timedelta(minutes=1), guild=self.server.guild,
                                     channel_name=self.channel2.channel_name)
        request = self.request_factory.post('/get-ad-engagement/', {"pk": self.adobject2.pk}, format='json')
        request.user = self.user
        view = get_activity_points
        response = view(request)
        self.assertTrue(response.data["points"]==204)
        self.assertTrue(response.status_code == status.HTTP_200_OK)



class CalculateIncomeTests(TestCase):

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        self.server = Servers.objects.create(owner=1, guild=1)
        self.adv_server = self.server.advserverinfo
        self.adv_server.current_cpm = 0.5
        self.adv_server.save()
        self.ad1 = Advertiser.objects.create(company_name="X", website="url", description="ElonsGang")
        self.advert1 = Ad.objects.create(company=self.ad1, text="Ad Text 1")
        self.channel1 = Channel.objects.create(server=self.adv_server, channel_name="Test", ad_frequency=20, ad_last_shown=timezone.now()-timedelta(minutes=3))


    def add_activity(self, unique_m, total_m, start_time, guild, channel_name):
        obj = {
            "unique_messages": unique_m,
            "total_messages": total_m,
            "start_time": start_time,
            "guild": guild,
            "channel_name": channel_name
        }
        request = self.request_factory.post('/add-activity/', obj, format='json')
        request.user = self.user
        view = add_server_activity
        response = view(request)
        return response

    def add_ads_and_activity(self, unique, ad_time):
        AdObject.objects.create(channel_pk=self.channel1.pk, server_id=self.server.guild, ad=self.advert1, time=ad_time)
        self.add_activity(unique, unique*2, ad_time, self.server.guild, self.channel1.channel_name)

    def test_calculating_earnings(self):
        self.add_ads_and_activity(30, (datetime.combine(datetime.today(), time.min)-timedelta(days=1)+timedelta(hours=6)).isoformat())
        self.add_ads_and_activity(60, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=12)).isoformat())
        self.add_ads_and_activity(90, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=18)).isoformat())
        self.add_ads_and_activity(45, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=14)).isoformat())
        self.add_ads_and_activity(67, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=9)).isoformat())
        seri = CalculateDailyIncomeSerializer()
        income = seri.get_daily_income(self.server.guild)
        self.assertTrue(income["earnings"]==876*0.5/1000)


    def test_daily_income_creation(self):
        self.add_ads_and_activity(30, (datetime.combine(datetime.today(), time.min)-timedelta(days=1)+timedelta(hours=6)).isoformat())
        self.add_ads_and_activity(60, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=12)).isoformat())
        self.add_ads_and_activity(90, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=18)).isoformat())
        self.add_ads_and_activity(45, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=14)).isoformat())
        self.add_ads_and_activity(67, (
                    datetime.combine(datetime.today(), time.min) - timedelta(days=1) + timedelta(hours=9)).isoformat())
        seri = CalculateDailyIncomeSerializer()
        income = seri.update_daily_income_of_servers()
        incomes = DailyIncome.objects.all()
        self.assertTrue(len(incomes)==1)
        self.assertTrue(incomes[0].cpm*incomes[0].engagement_points/1000==876*0.5/1000)
        self.assertTrue(incomes[0].adv_server==self.adv_server)
        #print(incomes[0].date)
        self.assertTrue(incomes[0].date==timezone.now().date()-timedelta(days=1))


class DailyIncomeTests(TestCase):

    """

    date = models.DateField()
    adv_server = models.ForeignKey(AdvServerInfo, on_delete=models.CASCADE, related_name="daily_incomes")
    engagement_points = models.IntegerField()
    cpm = models.FloatField()

    """


    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="Paul", password='my_secret')
        self.server = Servers.objects.create(owner=1, guild=1)
        self.adv_server = self.server.advserverinfo
        self.adv_server.current_cpm = 0.5
        self.adv_server.save()
        DailyIncome.objects.create(date=timezone.now().date()-timedelta(days=3),
                                   adv_server=self.adv_server,
                                   engagement_points=1000,
                                   cpm=0.5)
        DailyIncome.objects.create(date=timezone.now().date() - timedelta(days=4),
                                   adv_server=self.adv_server,
                                   engagement_points=700,
                                   cpm=0.4)
        DailyIncome.objects.create(date=timezone.now().date() - timedelta(days=5),
                                   adv_server=self.adv_server,
                                   engagement_points=2600,
                                   cpm=0.2)


    def test_get_daily_incomes(self):
        obj = {
            "guild": self.server.guild,
            "days": 4,
        }

        request = self.request_factory.post('/get-incomes/', obj, format='json')
        request.user = self.user
        view = get_daily_incomes_view
        response = view(request)
        data = response.data
        self.assertTrue(data[0]["earnings"] == 0.5)
        self.assertTrue(data[1]["engagement_points"] == 700)
        self.assertTrue(data[2]["cpm"] == 0.2)
