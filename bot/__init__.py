from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Status
from discord.ext.commands import Bot, Context
from discord.ext.commands import when_mentioned_or

from bot.utils import AsyncDatabase, Ready
from utils import on_vps


async def get_prefix(bot, message):
    return when_mentioned_or("&" if on_vps() else "%")(bot, message)


class Database(AsyncDatabase):
    def __init__(self, bot):
        super().__init__(bot)

        bot.scheduler.add_job(self.commit, CronTrigger(second=0))

    async def update(self):
        await self.commit()


class MainBot(Bot):
    def __init__(self):
        self.live = on_vps()
        self.client_id = 661972684153946122 if self.live else 663397340169764884

        self.ready = Ready()
        self.scheduler = AsyncIOScheduler()
        self.db = Database(self)

        super().__init__(command_prefix=get_prefix,
            owner_id=385807530913169426,
            status=Status.dnd)

    def setup(self):
        print("running setup...")

        for cog in self.ready.cogs:
            self.load_extension(f"cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    def run(self, version):
        self.version = version

        self.setup()

        with open(f"./data/token.{int(self.live)}", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print(f"running {'live' if self.live else 'prototype'} bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready.bot:
                await self.invoke(ctx)

            else:
                from utils.sendables import errmsg
                await ctx.send(errmsg("not ready"), delete_after=5)

    async def on_error(self, err, *args, **kwargs):
        error = self.get_cog("Error")
        await error.handle_error(err, *args, **kwargs)

    async def on_command_error(self, ctx, exc):
        error = self.get_cog("Error")
        await error.handle_command_error(ctx, exc)

    async def on_connect(self):
        print(f" bot connected (DWSP latency: {self.latency*1000:,.0f} ms)")

        if not self.ready.bot:
            await self.db.connect()
            await self.db.build()
            await self.db.update()
            print(f" connected to and updated database")

    async def on_disconnect(self):
        print(" bot disconnected")

    async def on_ready(self):
        if not self.ready.bot:
            self.scheduler.start()
            print(f" scheduler started ({len(self.scheduler.get_jobs()):,} job(s) scheduled)")

            while not self.ready.all:
                await sleep(1)

            self.ready.bot = True
            print(" bot ready")

        else:
            print(" bot reconnected")

        presence = self.get_cog("Presence")
        await presence.set()

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)


bot = MainBot()
