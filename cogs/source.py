from glob import glob
from json import load
from typing import Optional

from discord.ext.commands import Cog
from discord.ext.commands import command

from utils import match_files
from utils.menu import Menu, NumberedOptions
from utils.search import Search
from utils.sendables import embed

topics = {}

for file in match_files("./data/source/*.json"):
    with open(f"./data/source/{file}.json", "r", encoding="utf-8") as tf:
        topics.update({f"{k} ({file})": v for k, v in load(tf).items()})


class TopicMenu(Menu):
    def __init__(self, ctx, results):
        super().__init__(ctx)

        self.results = results

    async def start(self):
        options = NumberedOptions(self, self.results, "exit")
        await super().start("topic search", icon="info", lr=len(self.results), page=str(options), value=repr(options))

        if (r := await options.response()):
            if (num := r[-1]) in options.nlist:
                selection = options.option_n(num)

                links = [f"[{k}]({v})" for k, v in topics[str(selection)].items()]
                await self.update("topic source", clear=True, icon="info", topic=selection, links=" | ".join(links))

    async def stop(self):
        await self.message.delete()

    async def time_out(self):
        await self.message.delete()


class Source(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="source", aliases=["src"])
    async def get_source(self, ctx, *, topic: Optional[str]):
        if topic:
            results = Search(topic, topics.keys()).accurate_to(.7)

            if not len(results):
                await ctx.send(embed=embed("topic no results", ctx, icon="error"))

            elif len(results) == 1:
                links = [f"[{k}]({v})" for k, v in topics[str(results[0])].items()]
                await ctx.send(embed=embed("topic source", ctx, icon="info", topic=results[0], links=" | ".join(links)))

            else:
                await TopicMenu(ctx, results).start() 

        else:
            await ctx.send(embed=embed("no topic", ctx, icon="error"))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.bot:
            self.bot.ready.up(self)


def setup(bot):
    bot.add_cog(Source(bot))
