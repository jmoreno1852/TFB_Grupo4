# Guilds domain imports
from guilds.domain.entities import GuildMembership, Guild
from guilds.domain.ports import GuildRepository, MembershipRepository
from guilds.domain.errors import (
    GuildNotFoundError,
    AlreadyInGuildError,
    NotInGuildError,
    GuildAlreadyExistsError,
    InvalidGuildNameError,
    GuildHasMembersError,
)


class GuildsService:
    def __init__(
        self,
        guild_repository: GuildRepository,
        membership_repository: MembershipRepository,
    ):
        self.guild_repository = guild_repository
        self.membership_repository = membership_repository

    async def list_guilds(self):
        """List all available guilds (catalog)"""
        return await self.guild_repository.list_all()

    async def create_guild(self, name: str, description: str | None = None) -> Guild:
        name_norm = name.strip()
        if len(name_norm) < 3 or len(name_norm) > 50:
            raise InvalidGuildNameError("Guild name must be between 3 and 50 characters.")

        exists = await self.guild_repository.get_by_name(name_norm)
        if exists is not None:
            raise GuildAlreadyExistsError("A guild with this name already exists.")

        guild = Guild(
            id="",  # Mongo will generate
            name=name_norm,
            description=(description or "").strip() or None,
        )
        created = await self.guild_repository.create(guild)
        return created
    
    async def delete_guild(self, guild_id: str) -> None:
        guild_id_norm = guild_id.strip()

        guild = await self.guild_repository.get_by_id(guild_id_norm)
        if guild is None:
            raise GuildNotFoundError("Guild not found.")

        members_count = await self.membership_repository.count_members(guild_id_norm)
        if members_count > 0:
            raise GuildHasMembersError("To delete a guild member list should be empty.")

        await self.guild_repository.delete(guild)

    async def join_guild(self, user_id: str, guild_id: str) -> None:
        user_id_norm = user_id.strip()
        guild_id_norm = guild_id.strip()

        guild = await self.guild_repository.get_by_id(guild_id_norm)
        if guild is None:
            raise GuildNotFoundError("Guild not found.")

        existing = await self.membership_repository.get_membership(
            user_id_norm, guild_id_norm
        )
        if existing is not None:
            raise AlreadyInGuildError("User is already a member of this guild.")

        membership = GuildMembership(
            user_id=user_id_norm,
            guild_id=guild_id_norm,
        )
        await self.membership_repository.join(membership)

    async def leave_guild(self, user_id: str, guild_id: str) -> None:
        user_id_norm = user_id.strip()
        guild_id_norm = guild_id.strip()

        existing = await self.membership_repository.get_membership(
            user_id_norm, guild_id_norm
        )
        if existing is None:
            raise NotInGuildError("User is not a member of this guild.")

        await self.membership_repository.leave(user_id_norm, guild_id_norm)
