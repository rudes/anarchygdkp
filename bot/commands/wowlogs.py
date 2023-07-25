import discord
import logging

from util.wcl import WCLlogs
from util.view import WoWLog
from discord import SlashCommandGroup
from discord.ext import commands

log = logging.getLogger(__name__)

class Logs(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    logs = SlashCommandGroup('logs',
                             'Submit logs to Organizers, only accepts *Grobbulus* characters')

    @logs.command()
    async def submit(
        self,
        ctx: discord.ApplicationContext,
        character: discord.Option(str, "Exact name of your character on Grobbulus"),
        main: discord.Option(str, "optional Exact name of your main character on Grobbulus",
                             required=False),
        message: discord.Option(str, "optional message for Organizers", required=False),
        gold: discord.Option(discord.Attachment, "optional screenshot of Gold", required=False),
    ):
        """
        Submit your **Grobbulus** Character name for Organizers to evaluate
        """
        try:
            chat = ctx.guild.get_channel(int(self.config["CHANNELS"]["Logs"]))
            view = WoWLog(ctx.author, character, self.config)
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
            await ctx.author.edit(nick=character)
            await ctx.respond(f"Thank you for your submission. Changed your name to match {character}.", ephemeral=True, delete_after=5)
        except Exception as e:
            log.exception(f"submit,{type(e)},{e}")
