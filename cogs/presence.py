from discord import Activity, ActivityType
from discord.ext.commands import Cog
from discord.ext.commands import command


class Presence(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get(self):
        return

    async def set(self):
        await self.bot.change_presence(activity=Activity(name="&help", type=ActivityType.watching))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.bot:
            self.bot.ready.up(self)


def setup(bot):
    bot.add_cog(Presence(bot))
