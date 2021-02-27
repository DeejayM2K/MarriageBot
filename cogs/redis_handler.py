from datetime import datetime as dt

import discord
import voxelbotutils as utils

from cogs import utils as localutils


class RedisHandler(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.update_guild_prefix.start()
        self.update_max_family_members.start()
        self.update_incest_alllowed.start()
        self.update_max_children.start()
        self.update_gifs_enabled.start()
        self.send_user_message.start()
        self.redis_handler_DBLVote.start()
        self.redis_handler_ProposalCacheAdd.start()
        self.redis_handler_ProposalCacheRemove.start()
        self.redis_handler_TreeMemberUpdate.start()

    def cog_unload(self):
        self.update_guild_prefix.stop()
        self.update_max_family_members.stop()
        self.update_incest_alllowed.stop()
        self.update_max_children.stop()
        self.update_gifs_enabled.stop()
        self.send_user_message.stop()
        self.redis_handler_DBLVote.stop()
        self.redis_handler_ProposalCacheAdd.stop()
        self.redis_handler_ProposalCacheRemove.stop()
        self.redis_handler_TreeMemberUpdate.stop()

    @utils.redis_channel_handler("UpdateGuildPrefix")
    def update_guild_prefix(self, data):
        """
        Updates the prefix for the guild.
        """

        key = self.bot.config['guild_settings_prefix_column']
        data = data.get(key)
        self.bot.guild_settings[data['guild_id']][key] = data

    @utils.redis_channel_handler("UpdateFamilyMaxMembers")
    def update_max_family_members(self, data):
        """
        Updates the max number of family members for the guild.
        """

        data = data.get('max_family_members')
        self.bot.guild_settings[data['guild_id']]['max_family_members'] = data

    @utils.redis_channel_handler("UpdateIncestAllowed")
    def update_incest_alllowed(self, data):
        """
        Updates whether incest is allowed on guild.
        """

        data = data.get('allow_incest')
        self.bot.guild_settings[data['guild_id']]['allow_incest'] = data

    @utils.redis_channel_handler("UpdateMaxChildren")
    def update_max_children(self, data):
        """
        Updates the maximum children allowed per role in a guild.
        """

        prefix = data.get('max_children')
        if prefix is None:
            return
        self.bot.guild_settings[data['guild_id']]['max_children'] = prefix

    @utils.redis_channel_handler("UpdateGifsEnabled")
    def update_gifs_enabled(self, data):
        """
        Updates whether or not gifs are enabled for a guild.
        """

        prefix = data.get('gifs_enabled')
        if prefix is None:
            return
        self.bot.guild_settings[data['guild_id']]['gifs_enabled'] = prefix

    @utils.redis_channel_handler("SendUserMessage")
    async def send_user_message(self, payload):
        """
        Sends a message to a given user.
        """

        if self.bot.user.id != payload.get('bot_id', None):
            return
        if 0 not in (self.bot.shard_ids or [0]):
            pass
        try:
            user = await self.bot.fetch_user(payload['user_id'])
            await user.send(payload['content'])
            self.logger.info(f"Sent a DM to user ID {payload['user_id']}")
        except (discord.NotFound, discord.Forbidden, AttributeError):
            pass

    @utils.redis_channel_handler("DBLVote")
    def redis_handler_DBLVote(self, payload):
        self.bot.dbl_votes.__setitem__(payload['user_id'], dt.strptime(payload['datetime'], "%Y-%m-%dT%H:%M:%S.%f"))

    @utils.redis_channel_handler("ProposalCacheAdd")
    def redis_handler_ProposalCacheAdd(self, payload):
        self.bot.proposal_cache.raw_add(**payload)

    @utils.redis_channel_handler("ProposalCacheRemove")
    def redis_handler_ProposalCacheRemove(self, payload):
        self.bot.proposal_cache.raw_remove(*payload)

    @utils.redis_channel_handler("TreeMemberUpdate")
    def redis_handler_TreeMemberUpdate(self, payload):
        localutils.FamilyTreeMember(**payload)


def setup(bot:utils.Bot):
    x = RedisHandler(bot)
    bot.add_cog(x)
