from nextcord import slash_command
from nextcord.ext import commands
from bot.botNet import BotNet
from models.calendar import Calendar
from models.scheduler import Scheduler
from models.user_preferences import UserPreferences

import config
import datetime


class Technofutur(commands.Cog):
    def __init__(self, bot: BotNet):
        self.bot = bot
        self.calendar = Calendar()
        self.user_preferences = UserPreferences()
        self.scheduler = Scheduler(self.bot, self.calendar, self.user_preferences)

    @slash_command(
        name="techno_calendar",
        description="calendar technofutur",
        default_member_permissions=1,
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

    @slash_command(
        name="toggle_dm_notifications",
        description="Toggle DM notifications for daily lessons",
        default_member_permissions=0,
    )
    async def toggle_dm_notifications(self, interaction):
        """Toggle DM notifications for the user."""
        user_id = interaction.user.id
        enabled = self.user_preferences.toggle_dm_notifications(user_id)
        
        if enabled:
            await interaction.response.send_message(
                "✅ DM notifications enabled! You'll receive tomorrow's lessons via direct message.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "❌ DM notifications disabled! You'll no longer receive lessons via DM.",
                ephemeral=True,
            )


def setup(bot):
    bot.add_cog(Technofutur(bot))
