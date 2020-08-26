from datetime import datetime, timedelta

from SqlObjects import Raid
from discord.ext import commands
import discord
import re

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class Raids(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add_raid(self, ctx, *, msg):
        tokens = list(filter(None, re.split(',|, | ', msg)))
        error = True
        if tokens[1].lower() in weekdays:
            if re.match(r"^\d\d:\d\d$", tokens[2]):
                if len(tokens) >= 3:
                    Raid.raid_add(tokens[0], tokens[1], tokens[2], tokens[3:])
                    error = False
                else:
                    Raid.raid_add(tokens[0], tokens[1], tokens[2], "")
                    error = False
                await ctx.message.channel.send("Recorded Refinery Loading Information")

        if error:
            await ctx.message.channel.send("Could not record raid. \n"
                                           "Please use the format: '?add_raid CORP Weekday XX:XX' \n"
                                           "with systems being optionally listed at the end.")

    @commands.command()
    async def del_corp_sys(self, ctx, *, msg):
        if msg:
            tokens = list(filter(None, re.split(',|, | ', msg)))
            if not Raid.raid_for_corp(tokens[0]):
                await ctx.message.channel.send("Could not find any raids for saved for corp: " + tokens[0])
            elif tokens[1] in Raid.raid_for_corp(tokens[0]).systems:
                if len(tokens) >= 3:
                    Raid.raid_remove_sys(tokens[0], tokens[1:])
                else:
                    Raid.raid_remove_sys(tokens[0], tokens[1])
                await ctx.message.channel.send("Updated systems for: " + tokens[0])
            else:
                await ctx.message.channel.send("There was an issue processing your request. Please use format: \n"
                                               "?del_corp_sys CORP systems")
        else:
            await ctx.message.channel.send("There was an issue processing your request. Please use format: \n"
                                           "?del_corp_sys CORP systems")

    @commands.command()
    async def del_corp(self, ctx, *, msg):
        if msg:
            if not Raid.raid_for_corp(msg):
                await ctx.message.channel.send("Could not find any raids for saved for corp: " + msg)
            elif Raid.raid_del_corp(msg) > 0:
                await ctx.message.channel.send("Deleted Raids for: " + msg)
            else:
                await ctx.message.channel.send("There was an issue processing your request. Please use format: \n"
                                               "?del_corp CORP")
        else:
            await ctx.message.channel.send("There was an issue processing your request. Please use format: \n"
                                           "?del_corp CORP")

    @commands.command()
    async def add_corp_sys(self, ctx, *, msg):
        if msg:
            tokens = list(filter(None, re.split(',|, | ', msg)))
            if not Raid.raid_for_corp(tokens[0]):
                await ctx.message.channel.send("Could not find any raids for saved for corp: " + tokens[0])
            elif tokens[1] not in Raid.raid_for_corp(tokens[0]).systems:
                if len(tokens) >= 3:
                    Raid.raid_add_sys(tokens[0], tokens[1:])
                else:
                    Raid.raid_add_sys(tokens[0], tokens[1])
                await ctx.message.channel.send("Updated systems for: " + tokens[0])
            else:
                await ctx.message.channel.send("There was an issue processing your request. Please use format: \n"
                                               "?add_corp_sys CORP systems")
        else:
            await ctx.message.channel.send("There was an issue processing your request. Please use format: \n"
                                           "?add_corp_sys CORP systems")

    @commands.command()
    async def raids(self, ctx, *, msg=None):
        raids = []
        if not msg:
            now = datetime.utcnow().strftime("%A %H:%M")
            end = format((datetime.utcnow() + timedelta(hours=4)), '%A %H:%M')
            raids = Raid.raids_by_time(now, end)
            if raids.count():
                await ctx.message.channel.send("Listing raids scheduled to load within the next 4 hours.")
        if msg:
            if msg.strip().lower() in weekdays:
                raids = Raid.raids_by_day(msg.strip())
                if raids.first():
                    await ctx.message.channel.send("Listing raids scheduled to load on: " + msg)
            elif msg.strip().casefold() == "all".casefold():
                all_raids = Raid.raid_all()
                if all_raids.first():
                    for raid in all_raids.all():
                        if len(raid.systems) > 0:
                            await ctx.message.channel.send(
                                "Refinery for: " + raid.corp + " loading on " + raid.day_of_week
                                + " at " + raid.time + " in systems: " +
                                raid.systems.replace(",", ", "))
                        else:
                            await ctx.message.channel.send(
                                "Refinery for: " + raid.corp + " loading on " + raid.day_of_week
                                + " at " + raid.time)
            else:
                tokens = list(filter(None, re.split(',|, | ', msg)))
                raid = Raid.raid_for_corp(tokens[0])
                if raid:
                    if len(raid.systems) > 0:
                        await ctx.message.channel.send("Refinery for: " + raid.corp + " loading on " + raid.day_of_week
                                                       + " at " + raid.time + " in systems: " +
                                                       raid.systems.replace(",", ", "))
                    else:
                        await ctx.message.channel.send("Refinery for: " + raid.corp + " loading on " + raid.day_of_week
                                                       + " at " + raid.time)

        if raids.first():
            for raid in raids:
                if len(raid.systems) > 0:
                    await ctx.message.channel.send("Refinery for: " + raid.corp + " loading on " + raid.day_of_week +
                                                   " at " + raid.time + " in systems: " +
                                                   raid.systems.replace(",", ", "))
                else:
                    await ctx.message.channel.send("Refinery for: " + raid.corp + " loading on " + raid.day_of_week +
                                                   " at " + raid.time)
        else:
            await ctx.message.channel.send("Sorry, no raids were found.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            return


def setup(bot):
    bot.add_cog(Raids(bot))
