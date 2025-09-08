from nextcord import CustomActivity
import nextcord
from nextcord.ext import commands
import config


class BotNet(commands.Bot):
    def __init__(self):
        self.voice_client = None
        intents = nextcord.Intents.default()
        intents.members = True
        intents.voice_states = True
        intents.message_content = True
        super().__init__(
            intents=intents,
            activity=CustomActivity(
                name="Custom Status", state="Looking for his connection string"
            ),
        )

    async def on_ready(self):
        print(f"{self.user.display_name} est pret")
        if not config.DEBUG:
            guild = self.get_guild(int(config.CELLAR_GUILD_ID))
            if guild:
                await guild.get_channel(int(config.CHANNELBOT_LOG_ID)).send("UP !")

        self.cogs.get("Technofutur").scheduler.scheduler.start()
