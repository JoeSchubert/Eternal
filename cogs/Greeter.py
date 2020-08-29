import asyncio

from discord.ext import commands
import MiscFunctions as Util

coalition_chat = 653234239990661130
french_chat = 739552359692107888
german_chat = 739467024262103140


english_welcome = "Welcome to the Eternal Coalition Discord, please check out the <#749092528338239498> and  " \
                  "<#749092528338239498> channels, and ask any questions you may have, we have a lot of " \
                  "veteran pilots willing to help."

french_welcome = "Bienvenue sur le FTNL Discord, en partenariat avec les sociétés éternelles. Nous avons de " \
                 "nombreuses informations à lire dans la catégorie Base de connaissances et de nombreux pilotes " \
                 "expérimentés pour répondre à toutes vos questions. Veuillez lire le canal <#749092528338239498> " \
                 "pour savoir comment utiliser notre robot de traduction."

german_welcome = "Willkommen zum SPQR Discord, der mit den Eternal Corporations zusammenarbeitet. Wir haben viele " \
                 "Informationen in der Kategorie Knowledgebase zu lesen und viele erfahrene Piloten, um Ihre Fragen " \
                 "zu beantworten. Bitte lesen Sie den <#749092528338239498> -Kanal zur Verwendung unseres " \
                 "Übersetzer-Bots."


class Greeter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        new_role = Util.get_new_roles(before.roles, after.roles)
        if new_role == "Academy":
            await asyncio.sleep(20)
            roles = self.bot.get_guild(after.guild.id).get_member(after.id).roles
            for role in roles:
                # German Role Greeting
                if role.name == "German":
                    channel = self.bot.get_channel(german_chat)
                    await channel.send("<@!" + str(after.id) + ">" + german_welcome)
                # French Role Greeting
                if role.name == "French":
                    channel = self.bot.get_channel(french_chat)
                    await channel.send("<@!" + str(after.id) + ">" + french_welcome)
            channel = self.bot.get_channel(coalition_chat)
            await channel.send("<@!" + str(after.id) + ">" + english_welcome)


def setup(bot):
    bot.add_cog(Greeter(bot))
