import os
import discord
import logging
import configparser

from command import Logs
from discord.ext import commands

logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)-8s %(message)s",
                    filename="/var/log/gdkp_logeval.log", level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
discord_log = logging.getLogger("discord")
discord_log.setLevel(logging.ERROR)

config = configparser.ConfigParser()
config.read("bot.ini")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(debug_guilds=[1086303502894108783], intents=intents)

bot.add_cog(Logs(bot, config))

bot.run(str(os.environ["DISCORD_BOTKEY"]))
