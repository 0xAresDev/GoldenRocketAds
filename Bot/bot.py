from datetime import datetime, timezone, timedelta
from typing import Any

import discord
from discord import Interaction
from discord._types import ClientT
from requests.auth import HTTPBasicAuth
import requests
from discord.ext import commands, tasks

prefix = "*"
port = "8000"

intents = discord.Intents.all()
auth = HTTPBasicAuth("blank", "Password")
bot = commands.Bot(command_prefix=prefix, intents=intents)


def is_Owner(guild, sender):
    if guild.owner.id == sender.id:
        return True
    return False


@bot.event
async def on_guild_join(guild):
    obj = {
        "owner": guild.owner.id,
        "guild": guild.id
    }
    response = requests.post(f"http://127.0.0.1:{port}/server-owners/create-server/", obj, auth=auth)


@bot.event
async def on_guild_remove(guild):
    obj = {
        "sender": guild.owner.id,
        "guild": guild.id
    }
    response = requests.post(f"http://127.0.0.1:{port}/server-owners/delete-server/", obj, auth=auth)


channel_brief = "Change the Ad-Channels list"
# channel commands
@bot.command(name="channel", brief=channel_brief)
async def channel_commands(ctx, *args):
    if not is_Owner(ctx.guild, ctx.author):
        await ctx.send("No permission to do this!")
        return
    if len(args) == 0 or args[0] not in ["add", "remove", "update"]:
        await ctx.send(f"Invalid command, use {prefix}channel add, remove or update")
        return
    match args[0]:
        case "add":
            if len(args) != 3 or not args[2].isdigit():
                await ctx.send(
                    f"Invalid command, {prefix}channel add takes 2 arguments(channel name and ad_frequency in minutes)")
                return
            obj = {
                "channel": args[1],
                "ad_frequency": int(args[2]),
                "guild": ctx.guild.id
            }
            response = requests.post(f"http://127.0.0.1:{port}/server-owners/channels/", obj, auth=auth)
            if response.status_code == 201:
                await ctx.send(f"Added {str(args[1])}")
            else:
                await ctx.send(f"Error: Please try again!")
        case "remove":
            if len(args) != 2:
                await ctx.send(f"Invalid command, {prefix}channel remove takes 1 arguments(channel name)")
                return
            obj = {
                "channel": args[1],
                "guild": ctx.guild.id
            }
            response = requests.delete(f"http://127.0.0.1:{port}/server-owners/channels/", data=obj, auth=auth)
            if response.status_code == 200:
                await ctx.send(f"Removed {str(args[1])}")
            else:
                await ctx.send(f"Error: Please try again!")

        case "update":
            if len(args) != 4 or not args[3].isdigit():
                await ctx.send(
                    f"Invalid command, {prefix}channel update takes 3 arguments(old channel name, new channel name (old and new can be the same) and ad frequency in minutes)")
                return
            obj = {
                "old_channel": args[1],
                "new_channel": args[2],
                "ad_frequency": int(args[3]),
                "guild": ctx.guild.id
            }
            response = requests.put(f"http://127.0.0.1:{port}/server-owners/channels/", obj, auth=auth)
            if response.status_code == 200:
                await ctx.send(f"Changed {str(args[2])}")
            else:
                await ctx.send(f"Error: Please try again!")


advertisers_brief = "Change the Advertisers list"
# advertiser commands
@bot.command(name="advertisers", brief=advertisers_brief)
async def advertiser_commands(ctx, *args):
    if not is_Owner(ctx.guild, ctx.author):
        await ctx.send("No permission to do this!")
        return

    if len(args) < 1 or args[0] not in ["show", "add", "remove"]:
        await ctx.send(f"Invalid command, use {prefix}advertisers show, add or remove")
        return

    match args[0]:
        case "show":
            response = requests.get(f"http://127.0.0.1:{port}/ads/get-advertisers/", auth=auth)
            if response.status_code == 200:
                data = response.json()
                for ad in data:
                    await ctx.send(f"{ad['company_name']}\nWebsite: {ad['website']}\nDescription: {ad['description']}")
            else:
                await ctx.send(f"Error: Please try again!")

        case "add":
            if len(args) != 2:
                await ctx.send(f"Invalid command, {prefix}advertiser add takes 1 arguments(advertiser name)")
                return
            obj = {
                "ADD": args[1],
                "guild": ctx.guild.id
            }
            response = requests.patch(f"http://127.0.0.1:{port}/ads/change-advertisers-on-server/", data=obj, auth=auth)
            if response.status_code == 200:
                await ctx.send(f"Added {str(args[1])} as an advertiser on your server")
            else:
                await ctx.send(f"Error: Please try again!")
        case "remove":
            if len(args) != 2:
                await ctx.send(f"Invalid command, {prefix}advertiser remove takes 1 arguments(advertiser name)")
                return
            obj = {
                "REMOVE": args[1],
                "guild": ctx.guild.id
            }
            response = requests.patch(f"http://127.0.0.1:{port}/ads/change-advertisers-on-server/", obj, auth=auth)
            if response.status_code == 200:
                await ctx.send(f"Removed {str(args[1])} as an advertiser on your server")
            else:
                await ctx.send(f"Error: Please try again!")

income_brief = "Retrieve earnings"
# income commands
@bot.command(name="income", brief=income_brief)
async def income_commands(ctx, *args):
    if not is_Owner(ctx.guild, ctx.author):
        await ctx.send("No permission to do this!")
        return
    if len(args) != 1 or not args[0].isdigit():
        await ctx.send(f"Use {prefix}income [days] please!")
    obj = {
        "guild": ctx.guild.id,
        "days": args[0]
    }
    response = requests.post(f"http://127.0.0.1:{port}/revenue/get-incomes/", obj, auth=auth)
    if response.status_code == 200:
        for income in response.json():
            await ctx.send(f"Date: {income['date']}\nEngagement Points: {income['engagement_points']}\nCPM: {income['cpm']}\nEarnings: {income['earnings']}")
        if len(response.json()) == 0:
            await ctx.send("Income will be updated daily, wait until tomorrow please.")
    else:
        await ctx.send(f"Error: Please try again!")


class AdButton(discord.ui.Button):
    def __init__(self, label, url):
        super().__init__(url=url, label=label, style=discord.ButtonStyle.url)



class AdView(discord.ui.View):
    def __init__(self):
        super().__init__()

    def add_button(self, label, url):
        item = AdButton(label=label, url=url)  # Create an item to pass into the view class.
        self.add_item(item=item)


# loop that shows the tasks
@tasks.loop(minutes=1)
async def show_ads():
    for guild in bot.guilds:
        obj = {
            "guild": guild.id
        }
        response = requests.post(f"http://127.0.0.1:{port}/ads/get-ads/", obj, auth=auth)
        if response.status_code == 200:
            all_channels = guild.channels
            for channel in response.json().keys():
                for c in all_channels:
                    if channel == c.name:
                        data = response.json()[channel]
                        view = AdView()
                        for button in data["buttons"]:
                            view.add_button(button["label"], button["url"])
                        await c.send(data.get("text"), view=view)

start_time = datetime.now(timezone.utc)
activity_storage = {}

# loop for activities
@tasks.loop(minutes=5)
async def upload_activity():
    global start_time
    for guild in bot.guilds:
        #print(start_time)
        if guild.id in activity_storage.keys():
            for channel in guild.channels:
                #print(channel.id)
                if channel.id in activity_storage[guild.id].keys():
                    obj = {
                        "guild": guild.id,
                        "channel_name": channel.name,
                        "unique_messages": len(activity_storage[guild.id][channel.id]["senders"]),
                        "total_messages": activity_storage[guild.id][channel.id]["total"],
                        "start_time": start_time.isoformat()
                    }
                    #print(obj)
                    response = requests.post(f"http://127.0.0.1:{port}/revenue/add-activity/", obj, auth=auth)

                    """if response.status_code == 200:
                        all_channels = guild.channels
                        for channel in response.json().keys():
                            for c in all_channels:
                                if channel == c.name:
                                    data = response.json()[channel]
                                    view = AdView()
                                    for button in data["buttons"]:
                                        view.add_button(button["label"], button["url"])
                                    await c.send(data.get("text"), view=view)"""
    activity_storage.clear()
    start_time = datetime.now(timezone.utc)


# event when bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    show_ads.start()
    upload_activity.start()


# does x when message
@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    if message.guild.id not in activity_storage.keys():
        activity_storage[message.guild.id] = {}
    if message.channel.id not in activity_storage[message.guild.id].keys():
        activity_storage[message.guild.id][message.channel.id] = {"total": 0, "senders": set()}
    activity_storage[message.guild.id][message.channel.id]["total"] += 1
    activity_storage[message.guild.id][message.channel.id]["senders"].add(message.author.id)
    #print(activity_storage)
    await bot.process_commands(message)




bot.run('blank')
