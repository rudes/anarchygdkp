import os
import discord
import logging
import configparser

from wcl import WCLlogs
from discord import ButtonStyle

logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)-8s %(message)s",
                    filename="/var/log/gdkp_logeval.log", level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
discord_log = logging.getLogger('discord')
discord_log.setLevel(logging.ERROR)

config = configparser.ConfigParser()
config.read('bot.ini')

class WoWLog(discord.ui.View):
    def __init__(self, user: discord.Member, character: str):
        super().__init__()
        self.user = user
        url = f'https://classic.warcraftlogs.com/character/us/grobbulus/{character}'
        button = discord.ui.Button(label="Full Log", style=ButtonStyle.link, url=url)
        self.add_item(button)

    async def role_add(self, role: str):
        try:
            role = self.user.guild.get_role(int(config['ROLES'][role]))
            if role in self.user.roles:
                return
            await self.user.add_roles(role)
        except Exception as e:
            log.error(f"role_add,{type(e)},{e}")

    @discord.ui.button(label="Approved", style=ButtonStyle.primary)
    async def approve(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add('Approved')
        await interaction.response.send_message(f'{interaction.user.mention} gave {self.user.mention} Approved role.')
        self.stop()

    @discord.ui.button(label="Core", style=ButtonStyle.green)
    async def core(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add('Core')
        await interaction.response.send_message(f'{interaction.user.mention} gave {self.user.mention} Core role.')
        self.stop()

    @discord.ui.button(label="Decline", style=ButtonStyle.red)
    async def decline(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        try:
            await interaction.response.send_message(f'{interaction.user.mention} declined {self.user.mention}.')
            try:
                dm = await self.user.create_dm()
                await dm.send('Sorry you were declined based on your logs at this time. Please try again later. :)')
            except discord.Forbidden:
                pass
            self.stop()
        except Exception as e:
            log.error(f"decline,{type(e)},{e}")


intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(debug_guilds=[1130246056421109770], intents=intents)

wowlogs = bot.create_group('logs', 'Submit logs to Organizers, only accepts Grobbulus characters, use message for special circumstances')
@wowlogs.command()
async def submit(
    ctx: discord.ApplicationContext,
    character: discord.Option(str, "exact name of your character on wowlogs"),
    main: discord.Option(str, "optional exact name of your main character on grobbulus", required=False),
    message: discord.Option(str, "optional message for Organizers", required=False),
):
    try:
        chat = ctx.guild.get_channel(int(config['CHANNELS']['Logs']))
        view = WoWLog(ctx.author, character)
        raider = WCLlogs(character)
        post = f'User: {ctx.author.mention}'
        post += (f'\nCharacter: {raider.class_name} ({raider.spec}) '
               + f': {character} ({raider.historical_avg()}%)')
        if main:
            main_logs = WCLlogs(main)
            post += (f'\nMain: {main_logs.class_name} ({main_logs.spec}) '
                   + f': {main} ({main_logs.historical_avg()}%)')
        if message:
            post += f'\nMessage: {message}'
        await chat.send(post, view=view)
        await ctx.respond('Thank you for your submission.', ephemeral=True, delete_after=5)
    except Exception as e:
        log.error(f"submit,{type(e)},{e}")

bot.run(str(os.environ['DISCORD_BOTKEY']))
