# Pre-requisites
# pip install -U python-dotenv
# pip install -U discord.py
# pip install -U Pillow
# pip install sqlalchemy

# Set Discord Bot Token as Environmental Variable "ETERNAL_BOT_DISCORD_TOKEN"

import io
import os
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
from dotenv import load_dotenv

import FileUtils
import MiscFunctions
import TextTools
from SqlObjects import User

load_dotenv()
TOKEN = os.getenv('ETERNAL_BOT_DISCORD_TOKEN')

bot = commands.Bot(command_prefix='?', description='Eternal Bot')

# Guild ID for eternal ( this is currently set to a testing server)
eternal_guild = 739262594036006983
# Registration channel. Multiple channels can be listed separated by commas.
registration_channel_names = ["registration"]
registration_channel_ids = []
# Users in this role will be able to manage other user information within the bot
admin_role_names = ["HR"]
admin_role_ids = []


def timestamp():
    return datetime.utcnow().replace(microsecond=0).isoformat(' ')


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    print('------')


@bot.event
async def on_member_join(member):
    User.history_add(discord_id=member.id, server_id=member.guild.id, event="join", user_name=member.display_name,
                     timestamp=timestamp())


@bot.event
async def on_member_remove(member):
    User.history_add(discord_id=member.id, server_id=member.guild.id, event="leave", user_name=member.display_name,
                     timestamp=timestamp())


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        User.history_add(discord_id=after.id, server_id=after.guild.id, event="nick_change",
                         user_name=after.display_name, timestamp=timestamp())


@commands.guild_only()
@bot.command(name="toon",
             brief="Associates toons to users.",
             description="Associates toons to users.",
             usage="toon name *or* ?toon @user toon name",
             help="?toon name \n"
                   "    associates the specified toon to your account.\n"
                   "\n"
                   "?toon @user toon name\n"
                   "    associates the specified toon to the specified user.\n"
                   "    *this command can only be used by authorized users.*\n"
                   "\n"
                   "note: multiple toons can be added at once if separated by commas.")
async def toon(ctx, *, msg):
    if not ctx.message.mentions:
        user_toon = msg.strip()
        user = ctx.message.author.id
        if "," in user_toon:
            toons = user_toon.split(",")
            for x in toons:
                User.toon_add(user, ctx.message.guild.id, x.strip(), timestamp())
                await ctx.message.channel.send(
                    ctx.message.author.display_name + ", I have added characters: " + user_toon + " to your profile.")
        else:
            User.toon_add(user, ctx.message.guild.id, user_toon, timestamp())
            await ctx.message.channel.send(
                    ctx.message.author.display_name + ", I have added character: " + user_toon + " to your profile.")
    else:
        user = str(ctx.message.mentions[0].id)
        user_toon = msg.split(' ', 1)[1].strip()
        if MiscFunctions.role_name_has_access(admin_role_names, ctx.author.roles) or MiscFunctions.role_id_has_access(
                admin_role_ids, ctx.author.roles):
            if "," in user_toon:
                toons = user_toon.split(",")
                for x in toons:
                    User.toon_add(user, ctx.message.guild.id, x.strip(), timestamp())
                    await ctx.message.channel.send(
                        "Added characters: " + user_toon + " to user: <@!" + str(ctx.message.mentions[0].id) + ">")
            else:
                User.toon_add(user, ctx.message.guild.id, user_toon, timestamp())
                await ctx.message.channel.send(
                        "Added character: " + user_toon + " to user: <@!" + str(ctx.message.mentions[0].id) + ">")
        else:
            await ctx.message.channel.send(ctx.message.author.name + " Sorry, but you do not have access to this "
                                                                     "function. Contact a bot admin.")


@bot.command()
async def find_toon(ctx, *, msg):
    if not ctx.message.mentions:
        user_toon = msg.strip()
        results = User.toon_search(user_toon)
        if results.first() is not None:
            for x in results:
                await ctx.message.channel.send(
                    "Character: " + x.character + " was added to: <@!" + x.discord_id + "> on: " + x.timestamp)
        else:
            await ctx.message.channel.send("Could not find character: " + user_toon)
    else:
        user = str(ctx.message.mentions[0].id)
        results = User.toon_search_by_user(user)
        if results.first() is not None:
            for x in TextTools.list_toons(results):
                await ctx.message.channel.send(x)
        else:
            await ctx.message.channel.send("Could not find any characters for: <@!" + str(ctx.message.mentions[0].id) +
                                           ">")


@bot.command()
async def get_profile_image(ctx, *, msg):
    user_toon = msg.strip()
    if not ctx.message.mentions:
        if msg[0:3] == "<@!":
            user = msg[3:-1]
        else:
            result = User.toon_search(user_toon).first()
            user = result.discord_id
    else:
        user = str(ctx.message.mentions[0].id)

    if FileUtils.get_profile_image(user):
        limiter = 0
        for x in FileUtils.get_profile_image(user):
            if limiter < 3:
                file = discord.File(FileUtils.path + "/" + user + "/" + x, filename=x)
                await ctx.send(file=file, content="Uploaded: " + x[:-4])
                limiter += 1
            else:
                await ctx.message.channel.send("More than 3 images were found, limited to the first 3.")
                break
    else:
        if not ctx.message.mentions:
            await ctx.message.channel.send("Sorry, no profile images found associated with: " + user_toon)
        else:
            await ctx.message.channel.send("No profile images found associated with: <@!" +
                                           str(ctx.message.mentions[0].id) + ">")


# Override the Discord.py CommandNotFound error so that it does not spam with things that are not commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        return
    raise error


@bot.event
async def on_message(message):
    if message.channel.name in registration_channel_names or message.channel.id in registration_channel_ids:
        if message.attachments:
            f = io.BytesIO()
            image_types = ["png", "jpeg", "gif", "jpg"]
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(image) for image in image_types):
                    user = str(message.author.id)
                    filename = datetime.utcnow().strftime('%m-%d-%Y-%H-%M-%S') + ".png"
                    await attachment.save(f)
                    await FileUtils.resize_image(f, user, filename)
                    
    await bot.process_commands(message)


@bot.command()
async def summary(ctx, *, msg):
    user = ""
    user_toon = msg.strip()
    if not ctx.message.mentions:
        results = User.toon_search(user_toon)
        if results.first() is not None:
            for x in results:
                converter = MemberConverter()
                user = await converter.convert(ctx, x.discord_id)
                break
    else:
        user = ctx.message.mentions[0]
    user_summary = TextTools.list_summary(str(user.id), user.joined_at)
    for x in user_summary:
        await ctx.message.channel.send(x)
    await get_profile_image(ctx=ctx, msg=user.mention)

bot.run(TOKEN)
