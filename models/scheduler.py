from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from nextcord import TextChannel
import pytz

import datetime
import config

from models.calendar import Calendar
from models.user_preferences import UserPreferences
from bot.botNet import BotNet


class Scheduler:
    def __init__(self, bot: BotNet, calendar: Calendar, user_preferences: UserPreferences = None) -> None:
        self.calendar: Calendar = calendar
        self.bot: BotNet = bot
        self.user_preferences: UserPreferences = user_preferences
        self.announce_channel: TextChannel = None
        self.scheduler = AsyncIOScheduler()
        self.timezone = pytz.timezone('Europe/Brussels')  # Configure ton timezone ici
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
            CronTrigger(hour=16, minute=30, second=00, day_of_week="thu", timezone=self.timezone),
        )
        self.scheduler.add_job(
            self.__check_update_calendar,
            CronTrigger(hour=17, minute=00, second=00, timezone=self.timezone),
        )
        self.scheduler.add_job(
            self.__send_next_day_lesson,
            CronTrigger(hour=config.TECHNOFUTUR_NEXT_DAY_HOUR, minute=config.TECHNOFUTUR_NEXT_DAY_MINUTE, second=0, timezone=self.timezone),
        )
        print(f"[SCHEDULER] Jobs added with timezone: {self.timezone}")

    async def __get_calendar_channel(self) -> TextChannel:
        if not self.announce_channel:
            channel = await self.bot.fetch_channel(
                config.TECHNOFUTUR_CALENDAR_CHANNEL_ID
            )
            self.announce_channel = channel
        return self.announce_channel

    async def __get_week_calendar(self):
        try:
            print(f"[SCHEDULER] __get_week_calendar executed at {datetime.datetime.now(self.timezone)}")
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
        except Exception as e:
            print(f"[SCHEDULER] Error in __get_week_calendar: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    async def __check_update_calendar(self):
        try:
            print(f"[SCHEDULER] __check_update_calendar executed at {datetime.datetime.now(self.timezone)}")
            if week := self.calendar.is_updated():
                self.calendar.next_week = week

                msg = "@here\nThe schedule has been updated !!! :\n```" + \
                    str(week) + "```"
                channel = await self.__get_calendar_channel()
                await channel.send(msg)
        except Exception as e:
            print(f"[SCHEDULER] Error in __check_update_calendar: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    async def __send_next_day_lesson(self):
        """Send the lesson for tomorrow if there is one."""
        try:
            print("[SCHEDULER] __send_next_day_lesson called")
            next_day_lesson = self.calendar.get_next_day_lesson()
            print(f"[SCHEDULER] __send_next_day_lesson called - next_day_lesson: {next_day_lesson}")
            
            if next_day_lesson:
                print(f"[SCHEDULER] Lesson found: {next_day_lesson.lesson}")
            else:
                print("[SCHEDULER] No lesson found for tomorrow")
            
            if next_day_lesson and next_day_lesson.lesson and next_day_lesson.lesson != "No lesson":
                msg = f"📅 **Tomorrow's lesson:**\n```{str(next_day_lesson)}```"
                print(f"[SCHEDULER] Sending DM to users about tomorrow's lesson")
                
                # Send to users with DM notifications enabled
                if self.user_preferences:
                    dm_users = self.user_preferences.get_dm_users()
                    print(f"[SCHEDULER] Users with DM enabled: {dm_users}")
                    for user_id in dm_users:
                        try:
                            user = await self.bot.fetch_user(user_id)
                            await user.send(msg)
                            print(f"[SCHEDULER] DM sent successfully to user {user_id}")
                        except Exception as e:
                            print(f"[SCHEDULER] Error sending DM to user {user_id}: {e}")
                else:
                    print("[SCHEDULER] user_preferences is None!")
            else:
                print("[SCHEDULER] Condition failed - no DM will be sent")
        except Exception as e:
            print(f"[SCHEDULER] CRITICAL ERROR in __send_next_day_lesson: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
