from nextcord import slash_command, Option
from nextcord.ext import commands
from bot.botNet import BotNet
from models.calendar import Calendar
from models.scheduler import Scheduler
from models.user_preferences import UserPreferences
from views.technofutur import TimeModal

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
    async def toggle_dm_notifications(
        self,
        interaction,
        hour: int = Option(description="Hour (0-23)", required=False, min_value=0, max_value=23),
        minute: int = Option(description="Minute (0-59)", required=False, min_value=0, max_value=59),
    ):
        """Toggle DM notifications for the user with optional time setup."""
        user_id = interaction.user.id
        
        # Check if user already has notifications enabled
        if self.user_preferences.has_dm_notifications(user_id):
            # Disable notifications
            self.user_preferences.dm_users[user_id]["enabled"] = False
            self.user_preferences._UserPreferences__save_preferences()
            await interaction.response.send_message(
                "❌ DM notifications disabled! You'll no longer receive lessons via DM.",
                ephemeral=True,
            )
        else:
            # Enable notifications
            if hour is not None and minute is not None:
                # Use provided hour and minute directly
                success = self.user_preferences.set_dm_notification_time(user_id, hour, minute)
                if success:
                    await interaction.response.send_message(
                        f"✅ DM notifications enabled! You'll receive lessons at **{hour:02d}:{minute:02d}**.",
                        ephemeral=True,
                    )
                else:
                    await interaction.response.send_message(
                        "❌ Invalid time provided.",
                        ephemeral=True,
                    )
            else:
                # Enable notifications and show modal to set time
                enabled = self.user_preferences.toggle_dm_notifications(user_id)
                if enabled:
                    modal = TimeModal(self.user_preferences)
                    await interaction.response.send_modal(modal)

    @slash_command(
        name="set_notification_time",
        description="Set your preferred notification time for daily lessons",
        default_member_permissions=0,
    )
    async def set_notification_time(self, interaction):
        """Open modal to set notification time."""
        modal = TimeModal(self.user_preferences)
        await interaction.response.send_modal(modal)

    @slash_command(
        name="get_notification_time",
        description="Get your current notification time",
        default_member_permissions=0,
    )
    async def get_notification_time(self, interaction):
        """Get the user's current notification time."""
        user_id = interaction.user.id

        if self.user_preferences.has_dm_notifications(user_id):
            current_time = self.user_preferences.get_dm_notification_time(user_id)
            if current_time:
                hour, minute = current_time
                await interaction.response.send_message(
                    f"📅 Your notification time: **{hour:02d}:{minute:02d}**",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "❌ You haven't set a notification time yet. Use </set_notification_time:0> to set one.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "❌ You don't have DM notifications enabled. Use </toggle_dm_notifications:0> to enable them.",
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_ready(self):
        self.scheduler.start()


def setup(bot):
    bot.add_cog(Technofutur(bot))
