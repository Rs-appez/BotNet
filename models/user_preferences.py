import json
import os


class UserPreferences:
    """Manages user preferences for notifications."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.preferences_file = os.path.join(data_dir, "user_preferences.json")
        self.dm_users: set[int] = set()
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
                    self.dm_users = set(data.get("dm_users", []))
            except Exception as e:
                print(f"Error loading preferences: {e}")
                self.dm_users = set()

    def __save_preferences(self):
        """Save preferences to file."""
        self.__ensure_data_dir()
        try:
            with open(self.preferences_file, "w") as f:
                json.dump({"dm_users": list(self.dm_users)}, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def toggle_dm_notifications(self, user_id: int) -> bool:
        """
        Toggle DM notifications for a user.
        Returns True if notifications are now enabled, False if disabled.
        """
        if user_id in self.dm_users:
            self.dm_users.remove(user_id)
            enabled = False
        else:
            self.dm_users.add(user_id)
            enabled = True

        self.__save_preferences()
        return enabled

    def has_dm_notifications(self, user_id: int) -> bool:
        """Check if a user has DM notifications enabled."""
        return user_id in self.dm_users

    def get_dm_users(self) -> set[int]:
        """Get all users with DM notifications enabled."""
        return self.dm_users.copy()
