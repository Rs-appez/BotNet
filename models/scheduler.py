from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from nextcord import TextChannel

import datetime
import config

from models.calendar import Calendar
from bot.botNet import BotNet


class Scheduler:
    def __init__(self, bot: BotNet, calendar: Calendar) -> None:
        self.calendar: Calendar = calendar
        self.bot: BotNet = bot
        self.announce_channel: TextChannel = None
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
            CronTrigger(hour=23, minute=8, second=00, day_of_week="thu"),
        )
        self.scheduler.add_job(
            self.__check_update_calendar,
            CronTrigger(hour=17, minute=00, second=00),
        )

    async def __get_calendar_channel(self) -> TextChannel:
        if not self.announce_channel:
            channel = await self.bot.fetch_channel(
                config.TECHNOFUTUR_CALENDAR_CHANNEL_ID
            )
            self.announce_channel = channel
        return self.announce_channel

    async def __get_week_calendar(self):
        next_today = datetime.datetime.now() + datetime.timedelta(days=7)
        day = next_today.day
        month = next_today.month
        next_week = self.calendar.get_week(day, month)

        self.calendar.next_week = next_week

        if next_week:
            msg = "Here is the schedule for next week:\n```" + \
                str(next_week) + "```"
            channel = await self.__get_calendar_channel()
            await channel.send(msg)

    async def __check_update_calendar(self):
        if week := self.calendar.is_updated():
            self.calendar.next_week = week

            msg = "@here\nThe schedule has been updated !!! :\n```" + \
                str(week) + "```"
            channel = await self.__get_calendar_channel()
            await channel.send(msg)
