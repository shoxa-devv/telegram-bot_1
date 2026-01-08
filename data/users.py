import json
import os
from datetime import datetime, timedelta

USERS_FILE = "users.json"

# Premium Plan Constants
PLAN_FREE = "free"
PLAN_PRO = "pro"
PLAN_PRO_PLUS = "pro_plus"
PLAN_UNLIMITED = "unlimited"
PLAN_CUSTOM = "custom"

# Limits (messages per day)
LIMITS = {
    PLAN_FREE: 10,
    PLAN_PRO: 100,
    PLAN_PRO_PLUS: 250,
    PLAN_UNLIMITED: float("inf"),
    PLAN_CUSTOM: "custom",
}

# Prices (in Stars)
PRICES = {
    PLAN_PRO: 100,  # 100 Stars for Pro
    PLAN_PRO_PLUS: 250,  # 250 Stars for Pro+
    PLAN_UNLIMITED: 1000,  # 1000 Stars for Unlimited (Lifetime)
}


class UserManager:
    def __init__(self):
        self._load_users()

    def _load_users(self):
        if not os.path.exists(USERS_FILE):
            self.users = {}
        else:
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except Exception:
                self.users = {}

    def _save_users(self):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def get_user(self, user_id: int, username: str = None) -> dict:
        uid = str(user_id)
        if uid not in self.users:
            self.users[uid] = {
                "plan": PLAN_FREE,
                "subscription_end": None,
                "usage_date": datetime.now().date().isoformat(),
                "usage_count": 0,
                "image_usage_count": 0,
                "referral_count": 0,
                "username": username,
                "language": None,
            }
        else:
            if username:
                self.users[uid]["username"] = username

        # Migration: ensure key exists for old records
        if "referral_count" not in self.users[uid]:
            self.users[uid]["referral_count"] = 0
            self._save_users()
        if "username" not in self.users[uid]:
            self.users[uid]["username"] = username
            self._save_users()
        if "language" not in self.users[uid]:
            self.users[uid]["language"] = None
            self._save_users()
        if "blocked" not in self.users[uid]:
            self.users[uid]["blocked"] = False
            self._save_users()

        return self.users[uid]

    def set_language(self, user_id: int, language: str):
        uid = str(user_id)
        if uid not in self.users:
            self.get_user(user_id)
        self.users[uid]["language"] = language
        self._save_users()

    def get_language(self, user_id: int) -> str:
        uid = str(user_id)
        if uid not in self.users:
            return None
        return self.users[uid].get("language")

    def get_user_by_username(self, username: str) -> str:
        """Find user_id by username (without @)"""
        if not username:
            return None
        target = username.lower().replace("@", "")
        for uid, data in self.users.items():
            u = data.get("username", "")
            if u and u.lower().replace("@", "") == target:
                return uid
        return None

    def is_new_user(self, user_id: int) -> bool:
        return str(user_id) not in self.users

    def add_referral(self, user_id: int, referrer_id: int):
        uid = str(user_id)
        if uid not in self.users:
            self.get_user(user_id)

        if "referred_by" not in self.users[uid]:
            self.users[uid]["referred_by"] = referrer_id
            self._save_users()

            ref_uid = str(referrer_id)
            if ref_uid in self.users:
                self.users[ref_uid]["referral_count"] = self.users[ref_uid].get("referral_count", 0) + 1
                self._save_users()
                return True
        return False

    def get_referrer_info(self, user_id: int) -> dict:
        uid = str(user_id)
        if uid not in self.users:
            return None

        referrer_id = self.users[uid].get("referred_by")
        if referrer_id:
            return self.get_user(referrer_id)
        return None

    def check_limit(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        today = datetime.now().date().isoformat()

        if user.get("usage_date") != today:
            user["usage_date"] = today
            user["usage_count"] = 0
            user["image_usage_count"] = 0
            self._save_users()

        if user.get("subscription_end"):
            try:
                end_date = datetime.fromisoformat(user["subscription_end"])
                if datetime.now() > end_date:
                    user["plan"] = PLAN_FREE
                    user["subscription_end"] = None
                    if "custom_limit" in user:
                        del user["custom_limit"]
                    self._save_users()
            except ValueError:
                pass

        if "custom_limit" in user:
            base_limit = user["custom_limit"]
        else:
            base_limit = LIMITS.get(user.get("plan", PLAN_FREE), 10)

        if not isinstance(base_limit, (int, float)):
            base_limit = LIMITS[PLAN_FREE]

        extra_limit = user.get("referral_count", 0) * 3
        total_limit = base_limit + extra_limit

        # legacy VIP
        if str(user_id) == "1897652450":
            return True

        if total_limit == float("inf"):
            return True

        return user["usage_count"] < total_limit

    def increment_usage(self, user_id: int):
        user = self.get_user(user_id)
        user["usage_count"] = user.get("usage_count", 0) + 1
        self._save_users()

    def check_image_limit(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        today = datetime.now().date().isoformat()
        if user.get("usage_date") != today:
            self.check_limit(user_id)
            user = self.get_user(user_id)

        if str(user_id) == "1897652450":
            return True

        plan = user.get("plan", PLAN_FREE)
        if plan == PLAN_UNLIMITED:
            return True

        if plan == PLAN_FREE:
            limit = 3
        else:
            if "custom_limit" in user:
                base = user["custom_limit"]
            else:
                base = LIMITS.get(plan, 100)

            if not isinstance(base, (int, float)):
                base = 100

            limit = int(base * 0.5)

        return user.get("image_usage_count", 0) < limit

    def increment_image_usage(self, user_id: int):
        user = self.get_user(user_id)
        user["image_usage_count"] = user.get("image_usage_count", 0) + 1
        self._save_users()

    def set_plan(self, user_id: int, plan: str, duration_days: int = 30, custom_limit: int = None):
        uid = str(user_id)
        if uid not in self.users:
            self.get_user(user_id)

        self.users[uid]["plan"] = plan

        if custom_limit:
            self.users[uid]["custom_limit"] = custom_limit
        elif "custom_limit" in self.users[uid]:
            del self.users[uid]["custom_limit"]

        if plan == PLAN_UNLIMITED:
            expiry = datetime.now() + timedelta(days=365 * 100)
            self.users[uid]["subscription_end"] = expiry.isoformat()
        else:
            if duration_days:
                expiry = datetime.now() + timedelta(days=duration_days)
                self.users[uid]["subscription_end"] = expiry.isoformat()
            else:
                self.users[uid]["subscription_end"] = None

        self._save_users()

    def get_remaining_limit(self, user_id: int) -> int:
        user = self.get_user(user_id)

        if "custom_limit" in user:
            base_limit = user["custom_limit"]
        else:
            base_limit = LIMITS.get(user.get("plan", PLAN_FREE), 10)

        if not isinstance(base_limit, (int, float)):
            base_limit = LIMITS[PLAN_FREE]

        extra_limit = user.get("referral_count", 0) * 3
        total_limit = base_limit + extra_limit

        if total_limit == float("inf"):
            return 999999
        return max(0, total_limit - user.get("usage_count", 0))

    def block_user(self, user_id: int):
        uid = str(user_id)
        if uid not in self.users:
            self.get_user(user_id)
        self.users[uid]["blocked"] = True
        self._save_users()

    def unblock_user(self, user_id: int):
        uid = str(user_id)
        if uid in self.users:
            self.users[uid]["blocked"] = False
            self._save_users()

    def is_blocked(self, user_id: int) -> bool:
        uid = str(user_id)
        if uid not in self.users:
            return False
        return self.users[uid].get("blocked", False)

    def remove_premium(self, user_id: int):
        uid = str(user_id)
        if uid in self.users:
            self.users[uid]["plan"] = PLAN_FREE
            self.users[uid]["subscription_end"] = None
            self._save_users()


user_manager = UserManager()

