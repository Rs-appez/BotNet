import nextcord

from models.user_preferences import UserPreferences


class TimeModal(nextcord.ui.Modal):
    """Modal for users to input their preferred notification time."""

    def __init__(self, user_preferences: UserPreferences):
        super().__init__(title="Set Notification Time")
        self.user_preferences = user_preferences

        self.time_input = nextcord.ui.TextInput(
            label="Notification Time (HH:MM)",
            placeholder="23:00",
            min_length=5,
            max_length=5,
            required=True,
            default_value="23:00",
        )
        self.add_item(self.time_input)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        try:
            time_str = self.time_input.value
            hour, minute = map(int, time_str.split(":"))

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time format")

            success = self.user_preferences.set_dm_notification_time(
                interaction.user.id, hour, minute
            )

            if success:
                await interaction.response.send_message(
                    f"✅ Notification time set to **{hour:02d}:{minute:02d}**! You'll receive tomorrow's lessons at this time.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "❌ Invalid time format. Please use HH:MM (e.g., 09:30)",
                    ephemeral=True,
                )
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid time format. Please use HH:MM with hours 00-23 and minutes 00-59 (e.g., 09:30)",
                ephemeral=True,
            )
