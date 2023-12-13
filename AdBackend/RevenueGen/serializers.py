from rest_framework import serializers
from .models import DailyIncome, ChannelActivity
from ServerOwner.models import Servers, Channel
from django.utils import timezone
from datetime import timedelta, datetime, time
from Ads.models import AdObject

"""class DailyIncomeSerializers():

    def get_incomes(self, data):
        adv_server = Servers.objects.get(guild=data.get("guild")).advserverinfo
        daily_incomes = DailyIncome.objects.filter(adv_server=adv_server)
        incomes = []
        for income in daily_incomes:
            incomes.append({"date":income.date, "amount":income.amount})
        return incomes"""

class ChannelActivitySerializer():

    def create(self, data):
        if len(Channel.objects.filter(server=Servers.objects.get(guild=data.get("guild")).advserverinfo, channel_name=data.get("channel_name")))==0:
            return False

        total_m = data.get("total_messages")
        unique_m = data.get("unique_messages")
        channel = Channel.objects.get(server=Servers.objects.get(guild=data.get("guild")).advserverinfo, channel_name=data.get("channel_name"))

        last_activity = ChannelActivity.objects.filter(channel=channel)
        chunk = 0
        start = datetime.fromisoformat(data.get("start_time"))
        if len(last_activity)>0:
            last_activity = last_activity.latest("end_time")
            chunk = last_activity.chunk+1
        acti = ChannelActivity.objects.create(channel=channel, total_messages=total_m, unique_messagers=unique_m,
                                       start_time=start, chunk=chunk)

        if data.get("end_time"):
            end = datetime.strptime(data.get("end_time"), "%Y-%m-%dT%H:%M:%S.%f%z")
            acti.end_time = end
            acti.save()
        return True

class AdActivitySerializer():

    def get_activity(self, ad_object):
        channel = Channel.objects.filter(id=ad_object.channel_pk)
        if len(channel) != 1:
            return False
        channel = channel[0]
        time_ = ad_object.time

        difference_before = 5
        difference_after = 5
        iterations = 1
        stop = False
        sum_of_total_messages = 0
        sum_of_unique_messagers = 0

        while difference_before <= channel.ad_frequency/2 and difference_after <= channel.ad_frequency/2 and not stop:
            activities = ChannelActivity.objects.filter(channel=channel,
                                                        start_time__range=[time_-timedelta(minutes=difference_before),
                                                                           time_+timedelta(minutes=difference_after)])


            #print("Activity length: " + str(len(activities)))
            if len(activities) > 0:
                #print(activities)
                sum_of_total_messages = 0
                sum_of_unique_messagers = 0
                for act in activities:
                    #print("Current activity: ")
                    #print(act.start_time)
                    #print(act.end_time)
                    #print("\n")
                    sum_of_total_messages += act.total_messages
                    sum_of_unique_messagers += act.unique_messagers
                #print(sum_of_total_messages)
                #print(sum_of_unique_messagers)
                if sum_of_total_messages >= 50:
                    stop = True
                else:
                    difference_after += 5
                    difference_before += 5
                    iterations += 1
            else:
                difference_after += 5
                difference_before += 5
                iterations += 1
            #print(sum_of_unique_messagers)
            #print(sum_of_total_messages)
            #print(difference_before <= channel.ad_frequency/2 and difference_after <= channel.ad_frequency/2)
            #print(difference_before <= channel.ad_frequency/2 and difference_after <= channel.ad_frequency/2 and not stop)
            #print(iterations)
            #print(channel.ad_frequency)
        """print(f"Start: {(time_ - timedelta(minutes=difference_before))}")
        print(f"End: {(time_ + timedelta(minutes=difference_after))}")
        print("\n")"""

        engagement_points = sum_of_unique_messagers * max(1, 3/iterations)
        #print(str(sum_of_unique_messagers), str(engagement_points))
        return engagement_points


    def get_activity_points_in_specific_time_period(self, data):
        start = datetime.fromisoformat(data.get("start"))
        end = datetime.fromisoformat(data.get("end"))
        ad_objects = AdObject.objects.filter(server_id=data.get("guild"),  time__range=[start, end])
        points = 0
        for ad in ad_objects:
            p = self.get_activity(ad)
            if p:
                points += p
        return points


class CalculateDailyIncomeSerializer():
    act_seri = AdActivitySerializer()

    def get_daily_income(self, guild):
        obj = {
            "guild": guild,
            "start": (datetime.combine(datetime.today(), time.min)-timedelta(days=1)).isoformat(),
            "end": (datetime.combine(datetime.today(), time.max)-timedelta(days=1)).isoformat(),
        }
        engagement_points = self.act_seri.get_activity_points_in_specific_time_period(obj)

        cpm = Servers.objects.get(guild=guild).advserverinfo.current_cpm
        #print(engagement_points)
        response = {
            "engagement_points": engagement_points,
            "cpm": cpm,
            "earnings": engagement_points/1000 * cpm
        }
        return response


    def update_daily_income_of_servers(self):
        servers = Servers.objects.all()
        seri = CalculateDailyIncomeSerializer()
        for server in servers:
            income = seri.get_daily_income(server.guild)
            if income:
                DailyIncome.objects.create(date=timezone.now().date()-timedelta(days=1), adv_server=server.advserverinfo,
                                           engagement_points=income["engagement_points"], cpm=income["cpm"])
                return True
        return False

class DailyIncomeSerializer():

    def get_daily_incomes(self, guild, days):
        adv_server = Servers.objects.get(guild=guild).advserverinfo
        daily_incomes = DailyIncome.objects.filter(adv_server=adv_server).order_by("-date")
        if len(daily_incomes) >= days:
            daily_incomes = daily_incomes[0:days]
        incomes = []
        for income in daily_incomes:
            incomes.append({
                "date": str(income.date),
                "engagement_points": income.engagement_points,
                "cpm": income.cpm,
                "earnings": round(income.engagement_points/1000*income.cpm,2)
                            })
        return incomes
