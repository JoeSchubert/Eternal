from datetime import datetime, timedelta

from SqlObjects import Raid
from discord.ext import commands
import discord
import re

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

char_limit = 1800


def check_raid_channel(ctx):
    return ctx.message.channel.id == 749057646115422229


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
    @commands.check(check_raid_channel)
    async def add_raid(self, ctx, *, msg=""):
        error = True
        if msg:
            tokens = list(filter(None, re.split(',|, | ', msg)))
            if tokens[1].lower() in weekdays:
                if re.match(r"^\d\d\d\d$", tokens[2]):
                    time = tokens[2]
                    tokens[2] = time[:2] + ":" + time[2:]
                if re.match(r"^\d\d:\d\d$", tokens[2]):
                    if len(tokens) >= 3:
                        Raid.raid_add(tokens[0], tokens[1], tokens[2], tokens[3:])
                        error = False
                    else:
                        Raid.raid_add(tokens[0], tokens[1], tokens[2], "")
                        error = False
                    await ctx.message.channel.send("```Recorded Refinery Loading Information```")

            elif tokens[1].casefold() == "now".casefold():
                day = datetime.utcnow().strftime("%A")
                time = datetime.utcnow().strftime("%H:%M")
                if len(tokens) >= 2:
                    Raid.raid_add(tokens[0], day, time, tokens[2:])
                    error = False
                else:
                    Raid.raid_add(tokens[0], day, time, "")
                    error = False
                await ctx.message.channel.send("```Recorded Refinery Loading Information```")

        if error:
            await ctx.message.channel.send("```Could not record raid. \n"
                                           "Please use the format: '?add_raid CORP Weekday XX:XX' \n"
                                           "with systems being optionally listed at the end.```")

    @commands.command(name="del_corp_sys",
                      brief="Removes a system from an existing corp record.",
                      description="Removes a system from an existing corp record.",
                      usage="CORP systems",
                      help="Removes the specified systems from an existing CORP record \n"
                           "\n"
                           "Note: Multiple systems may be separated by commas.")
    @commands.check(check_raid_channel)
    async def del_corp_sys(self, ctx, *, msg=""):
        if msg:
            tokens = list(filter(None, re.split(',|, | ', msg)))
            if not Raid.raid_for_corp(tokens[0]).first():
                await ctx.message.channel.send("```Could not find any raids for saved for corp: " + tokens[0] + "```")
            elif tokens[1] in Raid.raid_for_corp(tokens[0]).first().systems:
                if len(tokens) >= 3:
                    Raid.raid_remove_sys(tokens[0], tokens[1:])
                else:
                    Raid.raid_remove_sys(tokens[0], tokens[1])
                await ctx.message.channel.send("```Updated systems for: " + tokens[0] + "```")
            else:
                await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                               "?del_corp_sys CORP systems```")
        else:
            await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                           "?del_corp_sys CORP systems```")

    @commands.command(name="del_raid",
                      brief="Removes an existing raid record.",
                      description="Remove an existing raid record.",
                      usage="CORP",
                      help="Removes the specified CORP's raid record.")
    @commands.check(check_raid_channel)
    async def del_raid(self, ctx, *, msg=""):
        if msg:
            if not Raid.raid_for_corp(msg).first():
                await ctx.message.channel.send("```Could not find any raids for saved for corp: " + msg + "```")
            elif Raid.raid_del_corp(msg) > 0:
                await ctx.message.channel.send("```Deleted Raids for: " + msg + "```")
            else:
                await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                               "?del_raid CORP```")
        else:
            await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                           "?del_raid CORP```")

    @commands.command(name="add_corp_sys",
                      brief="Adds a system to an existing corp record.",
                      description="Adds a system to an existing corp record.",
                      usage="CORP systems",
                      help="Adds the specified systems to an existing CORP record.\n"
                           "\n"
                           "Note: Multiple systems may be separated by commas.")
    @commands.check(check_raid_channel)
    async def add_corp_sys(self, ctx, *, msg=""):
        if msg:
            tokens = list(filter(None, re.split(',|, | ', msg)))
            if not Raid.raid_for_corp(tokens[0]).first():
                await ctx.message.channel.send("```Could not find any raids for saved for corp: " + tokens[0] + "```")
            elif tokens[1] not in Raid.raid_for_corp(tokens[0]).first().systems:
                if len(tokens) >= 2:
                    Raid.raid_add_sys(tokens[0], tokens[1:])
                else:
                    Raid.raid_add_sys(tokens[0], tokens[1])
                await ctx.message.channel.send("```Updated systems for: " + tokens[0] + "```")
            else:
                await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                               "?add_corp_sys CORP systems```")
        else:
            await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                           "?add_corp_sys CORP systems```")

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
                           "?raids CORP\n"
                           "Lists refinery records for a specific corp.\n"
                           "\n"
                           "?raids all\n"
                           "Lists all refinery records.")
    @commands.check(check_raid_channel)
    async def raids(self, ctx, *, msg=""):
        text_to_send = []
        raids = []
        target = ctx.message.channel
        if not msg:
            now = (datetime.utcnow() - timedelta(minutes=15)).strftime("%A %H:%M")
            end = format((datetime.utcnow() + timedelta(hours=4)), '%A %H:%M')
            raids = Raid.raids_by_time(now, end)
            if raids.first():
                text_to_send.append("Listing raids scheduled to load within the next 4 hours.\n")
        elif msg:
            if msg.strip().lower() in weekdays:
                raids = Raid.raids_by_day(msg.strip())
                if raids.first():
                    text_to_send.append("Listing raids scheduled to load on: " + msg + "\n")
            elif msg.strip().casefold() == "all".casefold():
                raids = Raid.raid_all()
                if raids.first():
                    text_to_send.append("Listing all refineries: \n")
            else:
                tokens = list(filter(None, re.split(',|, | ', msg)))
                raids = Raid.raid_for_corp(tokens[0])
        if raids.first():
            if raids.count() >= 10:
                await ctx.message.channel.send("```Results will be messaged to you as they exceed flood rate "
                                               "limits.```")
                target = await ctx.message.author.create_dm()
            for raid in raids:
                if len(raid.systems) > 0:
                    text_to_send.append(
                        "[" + raid.corp + "]" + " loads " + raid.day_of_week
                        + " at " + raid.time + "GT in systems: " +
                        raid.systems.replace(",", ", ") + " -- updated:" + raid.modified.strftime("(%m-%d)"))
                else:
                    text_to_send.append(
                        "[" + raid.corp + "]" + " loads " + raid.day_of_week
                        + " at " + raid.time + "GT -- updated:" + raid.modified.strftime("(%m-%d)"))
        else:
            if msg:
                await ctx.message.channel.send("```Sorry, no raids were found for: " + msg + "```")
            else:
                await ctx.message.channel.send("```Sorry, no raids were found.```")
        if text_to_send:
            await send_text(target, text_to_send)

    @commands.command(name="rename_corp",
                      brief="Renames an existing corp record.",
                      description="Renames an existing corp record.",
                      usage="OLD_CORP NEW_CORP",
                      help="Renames the specified OLD_CORP record with the NEW_CORP name.")
    @commands.check(check_raid_channel)
    async def rename_corp(self, ctx, *, msg=""):
        if msg:
            old_corp = msg.split(" ")[0]
            new_corp = msg.split(" ")[1]
            if not Raid.raid_for_corp(old_corp):
                await ctx.message.channel.send("```Could not find any raids for saved for corp: " + old_corp + "```")
            elif Raid.rename_corp(old_corp, new_corp):
                await ctx.message.channel.send("```Renamed Raids for: " + old_corp + " to: " + new_corp + "```")
            else:
                await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                               "?rename_corp OLD_CORP NEW_CORP```")
        else:
            await ctx.message.channel.send("```There was an issue processing your request. Please use format: \n"
                                           "?rename_corp OLD_CORP NEW_CORP```")

    @commands.Cog.listener()
    @commands.check(check_raid_channel)
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            return


async def send_text(target, text_to_send):
    if text_to_send:
        temp_text = ""
        for text in text_to_send:
            if len(temp_text) + len(text) <= char_limit:
                temp_text += text + "\n"
            else:
                await target.send("```\n" + temp_text + "\n```")
                temp_text = text
        if temp_text:
            await target.send("```\n" + temp_text + "\n```")


def setup(bot):
    bot.add_cog(Raids(bot))
