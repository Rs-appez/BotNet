from nextcord import slash_command
from nextcord.ext import commands
from bot.botNet import BotNet
from models.calendar import Calendar

import config
import datetime


class Technofutur(commands.Cog):
    def __init__(self, bot: BotNet):
        self.bot = bot
        self.calendar = Calendar()

    @slash_command(
        name="techno_calendar",
        description="calendar technofutur",
        default_member_permissions=0,
    )
    async def calendar(self, interaction):
        """Send the Technofutur calendar URL."""
        await interaction.response.send_message(
            f"https://docs.google.com/spreadsheets/d/{config.TECHNOFUTUR_CALENDAR_ID}",
            ephemeral=True,
        )

    @slash_command(
        name="get_current_technofutur_week",
        description="Get the current week lessons",
        default_member_permissions=0,
    )
    async def get_current_week(self, interaction):
        """Get the current week lessons."""
        await interaction.response.defer()

        today = datetime.datetime.now()
        day = today.day
        month = today.month
        current_week = self.calendar.get_week(day, month)

        if current_week:
            await interaction.followup.send("```" + str(current_week) + "```")
        else:
            await interaction.followup.send("No week corresponding to this week.")

    @slash_command(
        name="get_next_technofutur_week",
        description="Get the next week lessons",
        default_member_permissions=0,
    )
    async def get_next_week(self, interaction):
        """Get the next week lessons."""
        await interaction.response.defer()

        next_today = datetime.datetime.now() + datetime.timedelta(days=7)
        day = next_today.day
        month = next_today.month
        next_week = self.calendar.get_week(day, month)

        if next_week:
            await interaction.followup.send("```" + str(next_week) + "```")
        else:
            await interaction.followup.send("No week corresponding to the next week.")


def setup(bot):
    bot.add_cog(Technofutur(bot))
