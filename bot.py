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
discord_log = logging.getLogger("discord")
discord_log.setLevel(logging.ERROR)

config = configparser.ConfigParser()
config.read("bot.ini")

class WoWLog(discord.ui.View):
    def __init__(self, user: discord.Member, character: str):
        super().__init__(timeout=172800)
        self.user = user
        self.character = character

        url = f"https://classic.warcraftlogs.com/character/us/grobbulus/{character}"
        button = discord.ui.Button(label="Logs", style=ButtonStyle.link, url=url)
        self.add_item(button)

    async def role_add(self, role: str):
        try:
            role = self.user.guild.get_role(int(config["ROLES"][role]))
            if role is None:
                log.error(f"role_add,NoneRole,role not found in guild")
                return
            if role in self.user.roles:
                return
            await self.user.add_roles(role)
        except Exception as e:
            log.exception(f"role_add,{type(e)},{e}")

    @discord.ui.button(label="Approved", style=ButtonStyle.primary)
    async def approve(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add("Approved")
        await interaction.response.send_message(f"{interaction.user.mention} gave {self.user.mention} Approved role.")
        self.stop()

    @discord.ui.button(label="Core", style=ButtonStyle.green)
    async def core(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        await self.role_add("Core")
        await interaction.response.send_message(f"{interaction.user.mention} gave {self.user.mention} Core role.")
        self.stop()

    @discord.ui.button(label="Decline", style=ButtonStyle.red)
    async def decline(self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        try:
            await interaction.response.send_message(f"{interaction.user.mention} declined {self.user.mention}.")
            try:
                dm = await self.user.create_dm()
                msg = ("Currently we are rostering raiders with a stronger combination "
                       +"of Gear and Parses from the current phase of raids.\n"
                       +f"Make some improvements to **{self.character}** "
                       +"and come back for another shot :)")
                await dm.send(msg)
            except discord.Forbidden:
                pass
            self.stop()
        except Exception as e:
            log.exception(f"decline,{type(e)},{e}")


intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(debug_guilds=[1130246056421109770], intents=intents)

wowlogs = bot.create_group("logs", "Submit logs to Organizers, only accepts *Grobbulus* characters")
@wowlogs.command()
async def submit(
    ctx: discord.ApplicationContext,
    character: discord.Option(str, "Exact name of your character on Grobbulus"),
    main: discord.Option(str, "optional Exact name of your main character on Grobbulus", required=False),
    message: discord.Option(str, "optional message for Organizers", required=False),
    gold: discord.Option(discord.Attachment, "optional screenshot of Gold", required=False),
):
    """
    Submit your **Grobbulus** Character name for Organizers to evaluate
    """
    try:
        chat = ctx.guild.get_channel(int(config["CHANNELS"]["Logs"]))
        view = WoWLog(ctx.author, character)
        post = f"U: {ctx.author.mention}"
        try:
            r = WCLlogs(character)
            post += (f"\nR: {r.class_name} ({r.spec}): "
                + f"**{character}** ({r.highest_ilvl()} ilvl) "
                + f"({r.historical_avg()}%) ({r.heroic_count()}/5)")
        except IndexError:
            post += f"\nR: **{character}** missing current phase."

        if main:
            try:
                m = WCLlogs(main)
                post += (f"\nM: {m.class_name} ({m.spec}): "
                    + f"**{main}** ({m.highest_ilvl()} ilvl) "
                    + f"({m.historical_avg()}%) ({m.heroic_count()}/5)")
            except IndexError as e:
                post += f"\nM: **{main}** missing current phase."
        if message:
            post += f"\n*{message}*"
        if gold:
            gold_file = await gold.to_file(spoiler=True)
            await chat.send(post, view=view, file=gold_file)
        else:
            await chat.send(post, view=view)
        await ctx.respond("Thank you for your submission.", ephemeral=True, delete_after=5)
    except Exception as e:
        log.exception(f"submit,{type(e)},{e}")

bot.run(str(os.environ["DISCORD_BOTKEY"]))
