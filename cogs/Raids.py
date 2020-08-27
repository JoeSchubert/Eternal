from datetime import datetime, timedelta

from SqlObjects import Raid
from discord.ext import commands
import discord
import re

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class Raids(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_raid",
                      brief="Adds or Updates refinery loading information.",
                      description="Saves refinery information.",
                      usage="CORP Weekday XX:XX systems",
                      help="Saves refinery loading information for specified CORP alias, day and time. if the CORP "
                           "already has a record saved this will update it.\n"
                           "\n"
                           "Optional: 'systems' The systems which belong to this corp with refineries. Multiple "
                           "systems may be listed separated by commas.")
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

        elif tokens[1].casefold() == "now".casefold():
            day = datetime.utcnow().strftime("%A")
            time = datetime.utcnow().strftime("%H:%M")
            if len(tokens) >= 2:
                Raid.raid_add(tokens[0], day, time, tokens[2:])
                error = False
            else:
                Raid.raid_add(tokens[0], day, time, "")
                error = False
            await ctx.message.channel.send("Recorded Refinery Loading Information")

        if error:
            await ctx.message.channel.send("Could not record raid. \n"
                                           "Please use the format: '?add_raid CORP Weekday XX:XX' \n"
                                           "with systems being optionally listed at the end.")

    @commands.command(name="del_corp_sys",
                      brief="Removes a system from an existing corp record.",
                      description="Removes a system from an existing corp record.",
                      usage="CORP systems",
                      help="Removes the specified systems from an existing CORP record \n"
                           "\n"
                           "Note: Multiple systems may be separated by commas.")
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

    @commands.command(name="del_corp",
                      brief="Removes an existing corp record.",
                      description="Remove an existing corp record.",
                      usage="CORP",
                      help="Removes the specified CORP record.")
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

    @commands.command(name="add_corp_sys",
                      brief="Adds a system to an existing corp record.",
                      description="Adds a system to an existing corp record.",
                      usage="CORP systems",
                      help="Adds the specified systems to an existing CORP record.\n"
                           "\n"
                           "Note: Multiple systems may be separated by commas.")
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

    @commands.command(name="raids",
                      brief="Lists raid records.",
                      description="Lists loading times for corps with systems, if known.",
                      usage="(options)",
                      help="Without any options specified this lists any refineries that will be loading in the next 4 "
                           "hours. \n"
                           "\n"
                           "?raids Weekday\n"
                           "Lists all refinery records that will be loading on the specified day.\n"
                           "\n"
                           "?raids all\n"
                           "Lists all refinery records.")
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
