from typing import List
import requests
import config
import datetime


class Day:
    def __init__(
        self,
        day_name: str,
        month: int,
        day: int,
        lesson: str = "",
        teacher: str = "",
        location: str = "",
    ):
        self.day_name: str = day_name
        self.month: int = int(month)
        self.day: int = int(day)

        self.lesson: str = lesson
        self.teacher: str = teacher
        self.location: str = location

    def __str__(self):
        string = f"{self.day_name:<10} "
        if self.location:
            string += f" 🏢 {self.location:<10}"
        else:
            string += f" 🏠 {'home':<10}"

        string += f" -> {self.day:>2}/{self.month:<2}: "
        if self.lesson:
            string += f"{self.lesson:<20} "
        else:
            string += " Congé 🎉"
        return string

    def __eq__(self, other):
        if not isinstance(other, Day):
            return False
        return (
            self.day_name == other.day_name
            and self.month == other.month
            and self.day == other.day
            and self.lesson == other.lesson
            and self.location == other.location
        )


class Week:
    def __init__(self):
        self.days: List[Day] = []

    def add_day(self, day: Day):
        self.days.append(day)

    def has_day(self, day: int, mouth: int) -> bool:
        return any(((d.day == day) and (d.month == mouth)) for d in self.days)

    def __str__(self):
        return (
            "\n".join(str(day) for day in self.days[:5])
            if self.days
            else "No lessons this week"
        )

    def __eq__(self, other):
        if not isinstance(other, Week):
            return False
        return self.days == other.days


class Calendar:
    def __init__(self):
        self.weeks: List[Week] = []
        self.next_week: Week = None
        self.calendar_json = None

        self.__init_next_week()

    def __reset_calendar(self):
        self.__load_calendar()
        self.weeks = []

        current_week = Week()
        for i, r in enumerate(self.calendar_json):
            if i == 0:
                continue

            data = r["values"]
            day_name = data[0]["formattedValue"]

            day_date, month_date = tuple(data[1]["formattedValue"].split("/"))
            lesson = r["values"][2].get("formattedValue", "No lesson")
            teacher = r["values"][4].get("formattedValue", "")
            location = r["values"][5].get("formattedValue", "")

            current_week.add_day(
                Day(day_name, month_date, day_date, lesson, teacher, location)
            )
            if len(current_week.days) == 7:
                self.weeks.append(current_week)
                current_week = Week()

    def __load_calendar(self):
        url_request = f"{config.URL_SHEET_API}{
            config.TECHNOFUTUR_CALENDAR_ID
        }?includeGridData={True}&key={config.GOOGLE_API_KEY}"
        res = requests.get(url_request)
        if res.status_code != 200:
            raise Exception(f"Error loading calendar: {
                            res.status_code} - {res.text}")
        self.calendar_json = res.json()["sheets"][0]["data"][0]["rowData"]

    def __init_next_week(self):
        today = datetime.datetime.now()
        match today.weekday():
            case 3 | 4 | 5 | 6:
                today = today + datetime.timedelta(days=7)

        day = today.day
        month = today.month
        self.next_week = self.get_week(day, month)

    def get_week(self, day: int, month: int) -> Week:
        self.__reset_calendar()

        for week in self.weeks:
            if week.has_day(day, month):
                return week

    def is_updated(self) -> bool | Week:
        """
        Check if the calendar has been updated.
        If updated, return the new week, else return False.
        """
        if not self.next_week:
            return False

        week = self.get_week(
            self.next_week.days[0].day, self.next_week.days[0].month)
        if week != self.next_week:
            return week

        return False


if __name__ == "__main__":
    calendar = Calendar()
