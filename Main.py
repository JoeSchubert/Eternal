# Pre-requisites
# pip install -U python-dotenv
# pip install -U discord.py
# pip install -U Pillow

# Set Discord Bot Token as Environmental Variable "ETERNAL_BOT_DISCORD_TOKEN"

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import DB
import FileUtils
from datetime import datetime
import io

load_dotenv()
TOKEN = os.getenv('ETERNAL_BOT_DISCORD_TOKEN')

bot = commands.Bot(command_prefix='?', description='Eternal Bot')

database = r"eternal_bot.db"

conn = DB.connect(database)
DB.initialize(conn)

admin_role = "HR"
# User id for the admin. This will always allow this user to access commands as a failsafe.
admin_id = "265602626509340672"

registration_channel = "registration"


def timestamp():
    return datetime.utcnow().replace(microsecond=0).isoformat(' ')


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    print('------')


@bot.event
async def on_member_join(member):
    DB.insert_user_history(conn, member.id, member.guild, "join", member.display_name, timestamp())


@bot.event
async def on_member_remove(member):
    DB.insert_user_history(conn, member.id, member.guild, "leave", member.display_name, timestamp())


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        DB.insert_user_history(conn, after.id, after.guild, "nick_change", after.nick, timestamp())


@commands.guild_only()
@bot.command()
async def joined(ctx, member: discord.Member):
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))


@commands.guild_only()
@bot.command()
async def toon(ctx, *, msg):
    error = False
    if not ctx.message.mentions:
        user_toon = msg.strip()
        user = ctx.message.author.id
        if "," in user_toon:
            toons = user_toon.split(",")
            for x in toons:
                print(x.strip())
                error = DB.insert_user_character(conn, user, x.strip(), timestamp())
            if not error:
                await ctx.message.channel.send(
                    ctx.message.author.display_name + ", I have added characters: " + user_toon + " to your profile.")
        else:
            error = DB.insert_user_character(conn, user, user_toon, timestamp())
            if not error:
                await ctx.message.channel.send(
                    ctx.message.author.display_name + ", I have added character: " + user_toon + " to your profile.")
    else:
        user = str(ctx.message.mentions[0].id)
        user_toon = msg.split(' ', 1)[1].strip()
        role = discord.utils.get(ctx.guild.roles, name=admin_role)
        if role in ctx.author.roles or str(ctx.message.author.id) == admin_id:
            if "," in user_toon:
                toons = user_toon.split(",")
                for x in toons:
                    error = DB.insert_user_character(conn, user, x.strip(), timestamp())
                if not error:
                    await ctx.message.channel.send(
                        "Added characters: " + user_toon + " to user: <@!" + str(ctx.message.mentions[0].id) + ">")
            else:
                error = DB.insert_user_character(conn, user, user_toon, timestamp())
                if not error:
                    await ctx.message.channel.send(
                        "Added character: " + user_toon + " to user: <@!" + str(ctx.message.mentions[0].id) + ">")
        else:
            await ctx.message.channel.send(ctx.message.author.name + "Sorry, but you do not have access to this "
                                                                     "function. Contact a bot admin.")
    if error:
        await ctx.message.channel.send(ctx.message.author.name + "Sorry, there was an error completing your command.")


@bot.command()
async def toon_search(ctx, *, msg):
    user_toon = msg.strip()
    results = DB.search_user_character(conn, user_toon)
    if results:
        for x in results:
            await ctx.message.channel.send(
                "Character: " + x[2] + " was added to: <@!" + x[1] + "> on: " + x[3])
    else:
        await ctx.message.channel.send("Could not find character: " + user_toon)


@bot.command()
async def toons_for_user(ctx):
    if not ctx.message.mentions:
        await ctx.message.channel.send("You need to mention a user to use this command.")
    else:
        user = str(ctx.message.mentions[0].id)
        results = DB.search_characters_for_user(conn, user)
        if results:
            for x in results:
                await ctx.message.channel.send(
                     "Character: " + x[2] + " was added to: <@!" + x[1] + "> on: " + x[3])
        else:
            await ctx.message.channel.send("Could not find any characters for: <@!" + str(ctx.message.mentions[0].id) +
                                           ">")


@bot.command()
async def get_profile_image(ctx, *, msg):
    user = ""
    user_toon = msg.strip()
    if not ctx.message.mentions:
        results = DB.search_user_character(conn, user_toon)
        if results:
            for x in results:
                user = x[1]
                break
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
            await ctx.message.channel.send("Sorry, nothing found associated with: " + user_toon)
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
    if str(message.channel) == registration_channel:
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


bot.run(TOKEN)
