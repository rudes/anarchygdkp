import logging
import discord
import ButtonStyle

log = logging.getLogger(__name__)

class WoWLog(discord.ui.View):
    def __init__(self, user: discord.Member, character: str, config):
        super().__init__(timeout=172800)
        self.user = user
        self.character = character
        self.config = config

        url = f"https://classic.warcraftlogs.com/character/us/grobbulus/{character}"
        button = discord.ui.Button(label="Logs", style=ButtonStyle.link, url=url)
        self.add_item(button)

    async def role_add(self, role: str):
        try:
            role = self.user.guild.get_role(int(self.config["ROLES"][role]))
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
