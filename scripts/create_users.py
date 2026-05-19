import requests

import requests

BASE_URL = "http://localhost:8000"
PASSWORD = "Test1234"
NUM_USERS = 1000

for i in range(1, NUM_USERS + 1):
    email = f"test_user_{i}@test.com"

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
        },
        timeout=10,
    )

    print(i, email, response.status_code)

"""
    Guilds:
    BoosterGuild - 69e392eacf811b1dc6fd7d40 
    Sleepers Guild - 69e39322cf811b1dc6fd7d41
    Physical Guild - 69e392d1cf811b1dc6fd7cf4

    Quests:
    Booster Guild Quests:
{
  "guild_id": "69e392eacf811b1dc6fd7d40",
  "title": "Q3_BG",
  "description": "Booster Quest 3",
  "difficulty": 1,
  "xp_reward": 10000,
  "gold_reward": 10000,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}


Sleepers Guild Quests:
{
  "guild_id": "69e39322cf811b1dc6fd7d41",
  "title": "Cozy Setup",
  "description": "Avoid strong cold lights and screens at least 30 minutes before bedtime. Get Cozy!",
  "difficulty": 1,
  "xp_reward": 25,
  "gold_reward": 10,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}

{
  "guild_id": "69e39322cf811b1dc6fd7d41",
  "title": "A goods Day rest",
  "description": "Sleep at least 8 hours",
  "difficulty": 1,
  "xp_reward": 25,
  "gold_reward": 10,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}

{
  "guild_id": "69e39322cf811b1dc6fd7d41",
  "title": "Aftercare",
  "description": "Do your bed!",
  "difficulty": 1,
  "xp_reward": 25,
  "gold_reward": 10,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}

Physical Guild Quests- 69e02ee7da370bbc69c58d69
{
  "guild_id": "69e392d1cf811b1dc6fd7cf4",
  "title": "The Machine Stops... Or not.",
  "description": "Do 10000 steps.",
  "difficulty": 1,
  "xp_reward": 25,
  "gold_reward": 10,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}

{
  "guild_id": "69e392d1cf811b1dc6fd7cf4",
  "title": "Elastic Man",
  "description": "Strech 15 minutes today.",
  "difficulty": 1,
  "xp_reward": 25,
  "gold_reward": 10,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}

{
  "guild_id": "69e392d1cf811b1dc6fd7cf4",
  "title": "Go to the gym",
  "description": "You are being summoned... to lift some weights!",
  "difficulty": 3,
  "xp_reward": 50,
  "gold_reward": 100,
  "is_active": true,
  "weight": 1,
  "cooldown_hours": 0
}
"""
