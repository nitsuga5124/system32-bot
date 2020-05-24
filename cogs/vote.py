from discord.ext.commands import Cog
from discord.ext.commands import command


class Vote(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready.bot:
			self.bot.ready.up(self)


def setup(bot):
	bot.add_cog(Vote(bot))