import os
import discord
import logging
import configparser

from discord.ext import commands

logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)-8s %(message)s",
                    filename="/var/log/gdkp_logeval.log", level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
discord_log = logging.getLogger('discord')
discord_log.setLevel(logging.ERROR)

config = configparser.ConfigParser()
config.read('bot.ini')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(debug_guilds=[1130246056421109770], intents=intents)

group = bot.create_group('logs', 'Submit logs to Organizers.')
@group.command()
async def submit(
    ctx: discord.ApplicationContext,
    logs: Option(str, "url to your character on wowlogs"),
    message: Option(str, "optional message for Organizers")
):
    try:
        chat = ctx.guild.get_channel(int(config['CHANNELS']['Logs']))
        view = WoWLog(logs, message)
        await chat.send(view=view)
    except Exception as e:
        log.error(f"command,{type(e)} error occured,{e}")

bot.add_application_command(group)
bot.run(str(os.environ['DISCORD_BOTKEY']))

class WoWLog(discord.ui.View):
    def __init__(self, config, url, message, user: discord.Member):
        super().__init__()
        self.user = user
        self.config = config

    async def role_add(self, role: str):
        role = self.user.guild.get_role(int(self.config['ROLES'][role]))
        if role in self.user.roles:
            return
        await self.user.add_roles(role)

    @discord.ui.button(label="Approved")
    async def approve_callback(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add('Approved')

    @discord.ui.button(label="Core")
    async def core_callback(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add('Core')
