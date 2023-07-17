import os
import discord
import logging
import configparser

from wcl import parse_logs

logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)-8s %(message)s",
                    filename="/var/log/gdkp_logeval.log", level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
discord_log = logging.getLogger('discord')
discord_log.setLevel(logging.ERROR)

config = configparser.ConfigParser()
config.read('bot.ini')

class WoWLog(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__()
        self.user = user

    async def role_add(self, role: str):
        try:
            role = self.user.guild.get_role(int(config['ROLES'][role]))
            if role in self.user.roles:
                return
            await self.user.add_roles(role)
        except Exception as e:
            log.error(f"role_add,{type(e)},{e}")

    @discord.ui.button(label="Approved")
    async def approve(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add('Approved')
        await interaction.response.send_message(f'{interaction.user.mention} gave {self.user.mention} Approved role.')
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="Core")
    async def core(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add('Core')
        await interaction.response.send_message(f'{interaction.user.mention} gave {self.user.mention} Core role.')
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="Decline")
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
            await interaction.message.delete()
            self.stop()
        except Exception as e:
            log.error(f"decline,{type(e)},{e}")

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(debug_guilds=[1130246056421109770], intents=intents)

wowlogs = bot.create_group('logs', 'Submit logs to Organizers.')
@wowlogs.command()
async def submit(
    ctx: discord.ApplicationContext,
    logs: discord.Option(str, "exact name of your character on wowlogs"),
    message: discord.Option(str, "optional message for Organizers", required=False),
):
    try:
        chat = ctx.guild.get_channel(int(config['CHANNELS']['Logs']))
        view = WoWLog(ctx.author)
        avg = parse_logs(logs)
        await chat.send(f'User: {ctx.author.mention}\nLogs: {avg}\nMessage: {message}', view=view)
        await ctx.respond('Thank you for your submission.', ephemeral=True, delete_after=5)
    except Exception as e:
        log.error(f"submit,{type(e)},{e}")

bot.run(str(os.environ['DISCORD_BOTKEY']))
