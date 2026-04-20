from decouple import config

# debug
DEBUG = config("DEBUG", default=False)

# token
BOTNET_TOKEN = config("BOTNET_TOKEN")
GOOGLE_API_KEY = config("GOOGLE_API_KEY")

# guild
CELLAR_GUILD_ID = config("CELLAR_GUILD_ID", default=None)

# channels
CHANNELBOT_LOG_ID = 1110930833314938950
TECHNOFUTUR_CALENDAR_CHANNEL_ID = config("TECHNOFUTUR_CALENDAR_CHANNEL_ID")

# link
URL_SHEET_API = "https://sheets.googleapis.com/v4/spreadsheets/"

# technofutur
TECHNOFUTUR_CALENDAR_ID = config("TECHNOFUTUR_CALENDAR_ID", default=None)
TECHNOFUTUR_NEXT_DAY_HOUR = 23
TECHNOFUTUR_NEXT_DAY_MINUTE = 0
