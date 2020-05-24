from discord.ext.commands import Cog
from discord.ext.commands import command

from utils.sendables import infmsg


class Help(Cog):
	def __init__(self, bot):
		self.bot = bot

	# 	bot.remove_command("help")

	# @command(name="help")
	# async def display_help(self, ctx):
	# 	await ctx.send(infmsg("help"))

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready.bot:
			self.bot.ready.up(self)


def setup(bot):
	bot.add_cog(Help(bot))