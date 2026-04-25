import json
import os


class UserPreferences:
    """Manages user preferences for notifications."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.preferences_file = os.path.join(data_dir, "user_preferences.json")
        self.dm_users: dict = {}  # {user_id: {"hour": int, "minute": int, "enabled": bool}}
        self.__load_preferences()

    def __ensure_data_dir(self):
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def __load_preferences(self):
        """Load preferences from file."""
        self.__ensure_data_dir()
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, "r") as f:
                    data = json.load(f)
                    # Convert string keys to int keys
                    self.dm_users = {
                        int(k): v for k, v in data.get("dm_users", {}).items()
                    }
            except Exception as e:
                print(f"Error loading preferences: {e}")
                self.dm_users = {}

    def __save_preferences(self):
        """Save preferences to file."""
        self.__ensure_data_dir()
        try:
            with open(self.preferences_file, "w") as f:
                json.dump({"dm_users": self.dm_users}, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def set_dm_notification_time(self, user_id: int, hour: int, minute: int) -> bool:
        """
        Set the notification time for a user.
        Hour: 0-23, Minute: 0-59
        Returns True if notifications are enabled.
        """
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return False

        self.dm_users[user_id] = {
            "hour": hour,
            "minute": minute,
            "enabled": True,
        }
        self.__save_preferences()
        return True

    def toggle_dm_notifications(self, user_id: int) -> bool:
        """
        Toggle DM notifications for a user.
        Returns True if notifications are now enabled, False if disabled.
        """
        if user_id not in self.dm_users:
            # Initialize with default time (23:00) if not exists
            self.dm_users[user_id] = {
                "hour": 23,
                "minute": 0,
                "enabled": True,
            }
            enabled = True
        else:
            # Toggle enabled status
            self.dm_users[user_id]["enabled"] = not self.dm_users[user_id]["enabled"]
            enabled = self.dm_users[user_id]["enabled"]

        self.__save_preferences()
        return enabled

    def has_dm_notifications(self, user_id: int) -> bool:
        """Check if a user has DM notifications enabled."""
        return self.dm_users.get(user_id, {}).get("enabled", False)

    def get_dm_notification_time(self, user_id: int) -> tuple[int, int] | None:
        """
        Get the notification time for a user.
        Returns (hour, minute) or None if not set.
        """
        if user_id in self.dm_users:
            user_data = self.dm_users[user_id]
            return (user_data.get("hour", 23), user_data.get("minute", 0))
        return None

    def get_dm_users(self) -> dict:
        """Get all users with DM notifications enabled."""
        return {
            user_id: data
            for user_id, data in self.dm_users.items()
            if data.get("enabled", False)
        }
