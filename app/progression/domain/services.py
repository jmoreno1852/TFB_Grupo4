from app.progression.domain.entities import Progression, Stats
from app.progression.domain.ports import ProgressionRepository


class ProgressionService:
    def __init__(self, progression_repository: ProgressionRepository):
        self.progression_repository = progression_repository

    async def get_progress(self, user_id: str) -> Progression:
        """Get user progression with lazy initialization if missing"""
        user_id_norm = user_id.strip()
        return await self.progression_repository.get_by_user(user_id_norm)

    async def apply_rewards(self, user_id: str, xp: int, gold: int) -> Progression:
        """
        Apply rewards (XP + gold) to a user progression.
        - Applies XP and level-ups
        - Adds gold
        - Persists updated progression
        """
        #Normalize inputs
        user_id_norm = user_id.strip()
        xp_norm = max(0, int(xp))
        gold_norm = max(0, int(gold))

        prog = await self.progression_repository.get_by_user(user_id_norm)
        # Apply XP in specific function as we need to check for level ups and upgrade stats accordingly
        prog = self._apply_xp_and_levelups(prog, xp_norm)

        # Return updated instance with added gold and updated timestamp
        updated = Progression(
            user_id=prog.user_id,
            level=prog.level,
            xp=prog.xp,
            gold=prog.gold + gold_norm,
            stats=prog.stats,
            created_at=prog.created_at,
            updated_at=prog.updated_at,
        )

        await self.progression_repository.update_progression(updated)
        return updated

    def _apply_xp_and_levelups(self, prog: Progression, xp_to_add: int) -> Progression:
        """Apply XP and perform level-ups, granting +2 base stats per level."""
        if xp_to_add <= 0:
            return prog

        level = prog.level
        xp = prog.xp + xp_to_add
        stats = prog.stats

        while xp >= self.xp_required_for_next_level(level):
            required = self.xp_required_for_next_level(level)
            xp -= required
            level += 1

            stats = Stats(
                strength=stats.strength + 2,
                focus=stats.focus + 2,
                resilience=stats.resilience + 2,
            )

        return Progression(
            user_id=prog.user_id,
            level=level,
            xp=xp,
            gold=prog.gold,
            stats=stats,
            created_at=prog.created_at,
            updated_at=prog.updated_at,
        )

    def xp_required_for_next_level(self, level: int) -> int:
        """Centralized XP formula for next level."""
        level_norm = max(1, int(level))
        return 100 * level_norm
    
    async def spend_gold(self, user_id: str, amount: int) -> Progression:
        user_id_norm = user_id.strip()

        if amount <= 0:
            raise ValueError("amount must be > 0")

        return await self.progression_repository.spend_gold(
            user_id=user_id_norm,
            amount=amount,
        )
    #Function to check level, used by house
    async def get_level(self, user_id: str) -> int:
        """
        Return current user level.
        """
        user_id_norm = user_id.strip()
        prog = await self.progression_repository.get_by_user(user_id_norm)
        return prog.level