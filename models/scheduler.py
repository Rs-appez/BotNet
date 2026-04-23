from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from nextcord import TextChannel

import datetime
import config

from models.calendar import Calendar
from models.user_preferences import UserPreferences
from bot.botNet import BotNet


class Scheduler:
    def __init__(
        self, bot: BotNet, calendar: Calendar, user_preferences: UserPreferences = None
    ) -> None:
        self.calendar: Calendar = calendar
        self.bot: BotNet = bot
        self.user_preferences: UserPreferences = user_preferences
        self.announce_channel: TextChannel = None
        self.scheduler = AsyncIOScheduler()
        self.last_notification_day = None  # Track the last day we sent notifications
        self.__init_schedule()
        self.__add_jobs()

    def start(self):
        self.scheduler.start()

    def __init_schedule(self):
        job_defaults = {
            "coalesce": False,
            "max_instances": 1,
            "misfire_grace_time": 120,
        }
        self.scheduler.configure(job_defaults=job_defaults)

    def __add_jobs(self):
        if config.TECHNOFUTUR_CALENDAR_CHANNEL_ID:
            _ = self.scheduler.add_job(
                self.__get_week_calendar,
                CronTrigger(hour=16, minute=30, second=00, day_of_week="thu"),
            )
            _ = self.scheduler.add_job(
                self.__check_update_calendar,
                CronTrigger(hour=17, minute=00, second=00),
            )
        # Job that runs every minute to check for user-specific notification times
        _ = self.scheduler.add_job(
            self.__send_next_day_lesson_personalized,
            CronTrigger(minute="*"),  # Run every minute
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
            msg = "Here is the schedule for next week:\n```" + str(next_week) + "```"
            channel = await self.__get_calendar_channel()
            await channel.send(msg)

    async def __check_update_calendar(self):
        if week := self.calendar.is_updated():
            self.calendar.next_week = week

            msg = "@here\nThe schedule has been updated !!! :\n```" + str(week) + "```"
            channel = await self.__get_calendar_channel()
            await channel.send(msg)

    async def __send_next_day_lesson_personalized(self):
        """Send the lesson for tomorrow to users at their preferred time."""
        now = datetime.datetime.now()
        current_day = now.day

        next_day_lesson = self.calendar.get_next_day_lesson()

        if (
            next_day_lesson
            and next_day_lesson.lesson
            and next_day_lesson.lesson != "No lesson"
        ):
            msg = f"📅 **Tomorrow's lesson:**\n```{str(next_day_lesson)}```"

            # Send to users with DM notifications enabled
            if self.user_preferences:
                dm_users = self.user_preferences.get_dm_users()
                for user_id, user_data in dm_users.items():
                    notification_hour = user_data.get("hour", 9)
                    notification_minute = user_data.get("minute", 0)

                    # Check if it's the right time for this user
                    if (
                        now.hour == notification_hour
                        and now.minute == notification_minute
                        and self.last_notification_day != current_day
                    ):
                        try:
                            user = await self.bot.fetch_user(user_id)
                            await user.send(msg)
                            # Update the last notification day to avoid sending multiple times
                            self.last_notification_day = current_day
                        except Exception as e:
                            print(f"Error sending DM to user {user_id}: {e}")
