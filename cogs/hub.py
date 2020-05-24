from discord.ext.commands import Cog
from discord.ext.commands import command

from utils import on_vps
from utils.sendables import infmsg


class Hub(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.guild_id = 530249508177575952
		self.relay_id = 657612250768736271
		self.commands_id = 657611609094619146
		self.stdout_id = 657562932413988873 if on_vps() else 693455355216134214

	async def shutdown(self):
		print("shutting down...")
		await self.stdout.send(infmsg("shutting down", version=self.bot.version))

		await self.bot.logout()
		print(" logged out")

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready.bot:
			self.guild = self.bot.get_guild(self.guild_id)
			self.relay = self.bot.get_channel(self.relay_id)
			self.commands = self.bot.get_channel(self.commands_id)
			self.stdout = self.bot.get_channel(self.stdout_id)

			await self.stdout.send(infmsg("online", version=self.bot.version))
			self.bot.ready.up(self)

	@Cog.listener()
	async def on_message(self, msg):
		if not msg.author.bot and (self.bot.user in msg.mentions or "all" in msg.content):
			if msg.channel.id == self.commands.id:
				if msg.content.startswith("shutdown"):
					await self.shutdown()


def setup(bot):
	bot.add_cog(Hub(bot))