import random
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from app.quests.domain.entities import Quest, UserQuest
from app.quests.domain.errors import (
    QuestAlreadyCompletedError,
    QuestDeleteError,
    QuestNotAssignedError,
    QuestNotFoundError,
    QuestUpdateError,
)
from app.quests.domain.ports import (
    QuestCatalogRepository,
    RewardApplier,
    UserQuestRepository,
)


class QuestsService:
    def __init__(
        self,
        quest_catalog_repository: QuestCatalogRepository,
        user_quest_repository: UserQuestRepository,
        reward_applier: RewardApplier,
        active_quests_per_guild: int = 3, #Limit the number of active quests per guild 
        recent_completed_limit: int = 10, #Defined value to limit the number of recently completed quests
    ):
        self.quest_catalog_repository = quest_catalog_repository
        self.user_quest_repository = user_quest_repository
        self.reward_applier = reward_applier

        self.active_quests_per_guild = active_quests_per_guild
        self.recent_completed_limit = recent_completed_limit

    async def list_user_quests(self, user_id: str):
        """List active quests assigned to user from all the guilds the user belongs to """
        user_id_norm = user_id.strip()

        assigned = list(await self.user_quest_repository.list_active_by_user(user_id_norm))
        #Get list of quest ids to create catalog
        #uq stands for user quest
        quest_ids = [uq.quest_id for uq in assigned]
        if not quest_ids:
            return []
        #Create catalog with quests ids that are active and related to user
        catalog = list(await self.quest_catalog_repository.get_many_by_ids(quest_ids))
        catalog_by_id = {q.id: q for q in catalog}

        # Merge of catalog data and user quest, complete response of quest and information related to user.
        merged: list[dict[str, Any]] = []
        for uq in assigned:
            q = catalog_by_id.get(uq.quest_id)
            if q is None:
                # Catalog quest could be missing (delete case) skip it to avoid crashing listing.
                continue
            merged.append(
                {
                    "quest": q, #Complete Quest object
                    "assignment": uq, #UserQuest, containing information about the relation user <-> quest
                }
            )

        return merged

    async def complete_quest(self, user_id: str, quest_id: str) -> dict[str, Any]:
        """Complete an user quest with active status.
        Apply rewards defined in quest catalog and assignt new quest from same guild."""
        user_id_norm = user_id.strip()
        quest_id_norm = quest_id.strip()

        #Get active User Quest
        active = await self.user_quest_repository.get_active_assignment(user_id_norm, quest_id_norm)
        if active is None:
            #If there are none active we retrieve a list of completed quests to check if the quest was completed or is not assigned
            completed = await self.user_quest_repository.get_completed_assignment(user_id_norm, quest_id_norm)
            if completed is not None:
                raise QuestAlreadyCompletedError("Quest already completed.")
            raise QuestNotAssignedError("Quest is not assigned to user.")
        #Retrieve quest catalog to check for rewards and guild data
        quest = await self.quest_catalog_repository.get_by_id(quest_id_norm)
        if quest is None:
            raise QuestNotFoundError("Quest not found in catalog.")

        now = datetime.now(timezone.utc)
        #Complete quest and update date and status
        await self.user_quest_repository.mark_completed(user_id_norm, quest_id_norm, completed_at=now)

        # Rewards
        if quest.xp_reward:
            await self.reward_applier.add_xp(user_id_norm, quest.xp_reward)
        if quest.gold_reward:
            await self.reward_applier.add_gold(user_id_norm, quest.gold_reward)

        # Assign replacement quest from same guild
        new_quest = await self.pick_next_quest(user_id_norm, quest.guild_id)
        new_assignment = UserQuest(
            user_id=user_id_norm,
            guild_id=quest.guild_id,
            quest_id=new_quest.id,
        )
        await self.user_quest_repository.create_assignment(new_assignment)

        return {
            "completed_quest": quest,
            "rewards": {"xp": quest.xp_reward, "gold": quest.gold_reward},
            "new_assigned_quest": new_quest,
        }

    async def pick_next_quest(self, user_id: str, guild_id: str) -> Quest:
        """
        Pick next quest from the guild quest pool.
        Evaluations made:
        - Exclude quests that are currently active.
        - Exclude recently completed quests if cooldown is not defined.
        - Selection made based on weight in case we want to prioritize some quests
        """
        user_id_norm = user_id.strip()
        guild_id_norm = guild_id.strip()
        now = datetime.now(timezone.utc)
        #Get catalog of quests from a guild to create the pool
        pool = list(await self.quest_catalog_repository.list_active_by_guild(guild_id_norm))
        if not pool:
            raise QuestNotFoundError("No active quests available for this guild.")
        #Get list of quests from the guild that are assigned to the user
        active_assignments = list(
            await self.user_quest_repository.list_active_by_user_guild(user_id_norm, guild_id_norm)
        )
        #List of ids from the active quests
        active_ids = {uq.quest_id for uq in active_assignments}
        #List of recently completed quests to check cooldowns
        recent_completed = list(
            await self.user_quest_repository.list_recent_completed(
                user_id_norm, guild_id_norm, limit=self.recent_completed_limit
            )
        )
        completed_at_by_quest_id = {
            uq.quest_id: uq.completed_at for uq in recent_completed if uq.completed_at is not None
        }

        def cooldown_expired(q: Quest) -> bool:
            """Function to check the cooldown of the quests based on recently completed quests and cooldown defined in the guild's quest catalog"""
            completed_at = completed_at_by_quest_id.get(q.id)
            if completed_at is None:
                return True
            if q.cooldown_hours is None:
                return True
            return now >= (completed_at + timedelta(hours=q.cooldown_hours))
        #Select candidates from the pool based on quests that are not active and quests that are not in cooldown
        candidates = [q for q in pool if q.id not in active_ids and cooldown_expired(q)]

        #If we can't find quests that are not active and not in cooldown we ommit the cooldown requirement
        #We still ensure that the quests are not duplicated filtering by not active
        if not candidates:
            candidates = [q for q in pool if q.id not in active_ids]
        #Fallback error handling, should not happen normally
        if not candidates:
            raise QuestNotFoundError("No quests available to assign (all quests are already active).")
        #Use weighted value to select the quest from the candidates, default value of weight is 1
        return self._weighted_choice(candidates)


    async def bootstrap_guild_quests(self, user_id: str, guild_id: str) -> None:
        """Function called on join of the user to specific guild.
        It ensures the user has N active quests from the guild it joined."""
        user_id_norm = user_id.strip()
        guild_id_norm = guild_id.strip()
        #Get number of acrive quests for user <-> guild relationship
        current = await self.user_quest_repository.count_active(user_id_norm, guild_id_norm)
        #How many quests we need to reach the defined limit of active quests for specific guild
        missing = max(0, self.active_quests_per_guild - current)

        for _ in range(missing):
            next_quest = await self.pick_next_quest(user_id_norm, guild_id_norm)
            assignment = UserQuest(
                user_id=user_id_norm,
                guild_id=guild_id_norm,
                quest_id=next_quest.id,
            )
            await self.user_quest_repository.create_assignment(assignment)
    #This functions will be in public endpoints but in a future implementation they should only be accessible for admin status users
    async def create_quest(self, quest_data: dict[str, Any]) -> Quest:
        """Create quest for given guild's catalog"""
        guild_id = str(quest_data.get("guild_id", "")).strip()
        title = str(quest_data.get("title", "")).strip()
        if not guild_id or not title:
            raise QuestUpdateError("guild_id and title are required.")

        quest = Quest(
            id="",  # Mongo generates _id on insert
            guild_id=guild_id,
            title=title,
            description=(quest_data.get("description") or "").strip() or None,
            difficulty=int(quest_data.get("difficulty", 1)),
            xp_reward=int(quest_data.get("xp_reward", 10)),
            gold_reward=int(quest_data.get("gold_reward", 0)),
            is_active=bool(quest_data.get("is_active", True)),
            weight=quest_data.get("weight"),
            cooldown_hours=quest_data.get("cooldown_hours"),
        )
        return await self.quest_catalog_repository.create_quest(quest)

    async def update_quest(self, quest_id: str, quest_updates: dict[str, Any]) -> Quest:
        """Update data of specific quest in guild's catalog"""
        quest_id_norm = quest_id.strip()
        updated = await self.quest_catalog_repository.update_quest(quest_id_norm, quest_updates)
        if updated is None:
            raise QuestNotFoundError("Quest not found.")
        return updated

    async def delete_quest(self, quest_id: str) -> None:
        """Delete quest from guild's catalog"""
        quest_id_norm = quest_id.strip()
        existing = await self.quest_catalog_repository.get_by_id(quest_id_norm)
        if existing is None:
            raise QuestNotFoundError("Quest not found.")

        try:
            await self.quest_catalog_repository.delete_quest(quest_id_norm)
        except Exception as exc:  # persistence errors
            raise QuestDeleteError("Failed to delete quest.") from exc

    @staticmethod
    def _weighted_choice(quests: Iterable[Quest]) -> Quest:
        items = list(quests)
        weights = [(q.weight if isinstance(q.weight, int) and q.weight > 0 else 1) for q in items]
        return random.choices(items, weights=weights, k=1)[0]