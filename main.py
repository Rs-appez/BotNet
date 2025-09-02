import os
import config
from bot.botNet import BotNet

from speakNextcordBot.init_cog import init_cog

debug = config.DEBUG

botNet = BotNet()

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        botNet.load_extension(f"cogs.{file[:-3]}")

init_cog(botNet)

botNet.run(config.BOTNET_TOKEN)
