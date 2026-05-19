import csv
import random
from itertools import cycle
from threading import Lock

from locust import HttpUser, task, between


# =========================
# Test data
# =========================

GUILD_IDS = [
    "69e392eacf811b1dc6fd7d40",  # BoosterGuild
    "69e39322cf811b1dc6fd7d41",  # Sleepers Guild
    "69e392d1cf811b1dc6fd7cf4",  # Physical Guild
]


# =========================
# CSV loader
# =========================

def load_users_from_csv(path: str = "users.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


TEST_USERS = load_users_from_csv("users.csv")

_user_cycle = cycle(TEST_USERS)
_user_lock = Lock()


def get_next_user():
    with _user_lock:
        return next(_user_cycle)


# =========================
# Locust user
# =========================

class TFBUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.creds = get_next_user()
        self.joined_guild = False
        self.guild_id = None
        self.logged_in = False

        self.login()

        if not self.logged_in:
            return

        self.client.get("/users/me", name="GET /users/me")
        self.client.get("/guilds", name="GET /guilds")
        self.ensure_joined_guild()

    def login(self):
        with self.client.post(
            "/auth/login",
            json={
                "email": self.creds["email"],
                "password": self.creds["password"],
            },
            name="POST /auth/login",
            catch_response=True,
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Login failed: {response.status_code} {response.text}"
                )
                self.logged_in = False
                return

            try:
                data = response.json()
                token = data["access_token"]
            except Exception:
                response.failure("Invalid JSON in login response")
                self.logged_in = False
                return

            self.client.headers.update({
                "Authorization": f"Bearer {token}"
            })
            self.logged_in = True

    def ensure_joined_guild(self):
        if self.joined_guild or not self.logged_in:
            return

        guild_id = random.choice(GUILD_IDS)

        with self.client.post(
            "/guilds/join",
            json={"guild_id": guild_id},
            name="POST /guilds/join",
            catch_response=True,
        ) as response:

            if response.status_code in (204, 409):
                self.joined_guild = True
                self.guild_id = guild_id
                response.success() 

            else:
                response.failure(
                    f"Join guild failed: {response.status_code} {response.text}"
                )

    @task(6)
    def browse_core(self):
        if not self.logged_in:
            return

        self.client.get("/users/me", name="GET /users/me")
        self.client.get("/guilds", name="GET /guilds")
        self.client.get("/progression/me", name="GET /progression/me")

    @task(5)
    def quests_flow(self):
        if not self.logged_in:
            return

        response = self.client.get("/quests", name="GET /quests")
        if response.status_code != 200:
            return

        try:
            data = response.json()
        except Exception:
            return

        quests = data.get("quests", [])
        if not quests:
            return

        quest = random.choice(quests)
        quest_id = quest.get("id")
        if not quest_id:
            return

        self.client.post(
            f"/quests/{quest_id}/complete",
            name="POST /quests/{quest_id}/complete",
        )

    @task(3)
    def shop_flow(self):
        if not self.logged_in:
            return

        response = self.client.get("/shop/items", name="GET /shop/items")

        if response.status_code != 200:
            return

        try:
            data = response.json()
        except Exception:
            return

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("items", [])
        else:
            return

        if not items:
            return

        item = random.choice(items)

        item_id = item.get("item_id") or item.get("id")

        with self.client.post(
        "/shop/purchase",
        json={"item_id": item_id, "quantity": 1},
        name="POST /shop/purchase",
        catch_response=True,
        ) as response:

            if response.status_code == 200:
                response.success()

            elif response.status_code == 409:
                response.success()

            else:
                response.failure()

    @task(3)
    def inventory_flow(self):
        if not self.logged_in:
            return

        response = self.client.get("/inventory/me", name="GET /inventory/me")

        if response.status_code != 200:
            return

        try:
            data = response.json()
        except Exception:
            return

        items = data.get("items", [])

        owned_items = [
            item for item in items
            if item.get("quantity", 0) > 0 and item.get("equippable_slot")
        ]

        if not owned_items:
            return

        selected_item = random.choice(owned_items)

        self.client.post(
            "/inventory/equip",
            json={
                "item_id": selected_item["item_id"],
                "slot": selected_item["equippable_slot"],
            },
            name="POST /inventory/equip",
        )

    @task(2)
    def house_flow(self):
        if not self.logged_in:
            return

        self.client.get("/house/me", name="GET /house/me")

    @task(1)
    def maybe_join_guild(self):
        if not self.logged_in:
            return

        if not self.joined_guild:
            self.ensure_joined_guild()