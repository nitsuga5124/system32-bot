from datetime import datetime
from json import load, dump
from os.path import isfile
from random import randint
from traceback import format_exc

from discord.ext.commands import Cog
from discord.ext.commands import command

from discord import Forbidden
from discord.ext.commands import Cog, Context
from discord.ext.commands import command
from discord.ext.commands import (CommandNotFound, BadArgument, CheckFailure,
    MissingRequiredArgument, TooManyArguments, CommandOnCooldown)

from utils.chron import long_date_and_time, short_delta
from utils.sendables import errmsg


class Error(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = "./data/error_log.json"

    async def open_log(self):
        if isfile(self.path):
            with open(self.path, "r", encoding="utf-8") as lf:
                return load(lf)

        else:
            return {}

    async def save_log(self, log):
        with open(self.path, "w", encoding="utf-8") as lf:
            dump(log, lf, ensure_ascii=False)

    async def record_error(self, obj):
        hub = self.bot.get_cog("Hub")
        log = await self.open_log()

        msg = obj.message.content if obj and isinstance(obj, Context) else "Not applicable."

        while (ref := hex(randint(0x100000, 0xFFFFFF))[2:]) in log.keys():
            continue

        log.update({
            ref: {
                "content": msg,
                "err_time": long_date_and_time(datetime.utcnow()),
                "traceback": format_exc()
            }
        })

        await self.save_log(log)

        return ref

    async def handle_error(self, err, *args, **kwargs):
        hub = self.bot.get_cog("Hub")
        ref = await self.record_error(args[0] if len(args) > 0 else None)

        await hub.stdout.send(errmsg("something went wrong", ref=ref))

        if err == "on_command_error":
            await args[0].send(errmsg("command went wrong", ref=ref))

        raise

    async def handle_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif hasattr(exc, "key"):
            await ctx.send(errmsg(exc.key, **exc.kwargs))

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(errmsg("missing required argument"))

        elif isinstance(exc, BadArgument):
            await ctx.send(errmsg("bad argument"))

        elif isinstance(exc, TooManyArguments):
            await ctx.send(errmsg("too many arguments"))

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(errmsg("command on cooldown",
                length=short_delta(timedelta(seconds=exc.retry_after))))

        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send(errmsg("forbidden"))
                raise exc.original

            else:
                raise exc.original

        else:
            raise exc

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.bot:
            self.bot.ready.up(self)


def setup(bot):
    bot.add_cog(Error(bot))
