from decouple import config

# debug
DEBUG = config("DEBUG", default=False)

# token
BOTNET_TOKEN = config("BOTNET_TOKEN")
GOOGLE_API_KEY = config("GOOGLE_API_KEY")

# channels
CHANNELBOT_LOG_ID = 1110930833314938950
TECHNOFUTUR_CALENDAR_CHANNEL_ID = config(
    "TECHNOFUTUR_CALENDAR_CHANNEL_ID", default=None
)

# link
URL_SHEET_API = "https://sheets.googleapis.com/v4/spreadsheets/"

# technofutur
TECHNOFUTUR_CALENDAR_ID = config("TECHNOFUTUR_CALENDAR_ID", default=None)
