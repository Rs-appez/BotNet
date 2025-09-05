from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import datetime
import config

from models.calendar import Calendar
from bot.botNet import BotNet


class Scheduler:
    def __init__(self, bot: BotNet, calendar: Calendar) -> None:
        self.calendar = calendar
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.__init_schedule()
        self.__add_jobs()

    def __init_schedule(self):
        job_defaults = {
            "coalesce": False,
            "max_instances": 1,
            "misfire_grace_time": 120,
        }
        self.scheduler.configure(job_defaults=job_defaults)

    def __add_jobs(self):
        self.scheduler.add_job(
            self.__get_week_calendar,
            CronTrigger(hour=16, minute=30, second=00, day_of_week="thu"),
        )

    async def __get_week_calendar(self):
        next_today = datetime.datetime.now() + datetime.timedelta(days=7)
        day = next_today.day
        month = next_today.month
        next_week = self.calendar.get_week(day, month)

        announce_channel = self.bot.get_channel(config.TECHNOFUTUR_CALENDAR_CHANNEL_ID)

        if next_week and announce_channel:
            msg = "Here is the schedule for next week:\n```" + str(next_week) + "```"
            await announce_channel.send(msg)
