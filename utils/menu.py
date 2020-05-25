from asyncio import TimeoutError
from datetime import timedelta

from utils.chron import long_delta
from utils.emoji import get_emoji, mention_emoji
from utils.sendables import embed

class Menu(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.last_key = "placeholder"
        self.last_kwargs = {}

    async def start(self, key, **kwargs):
        self.message = await self.ctx.send(embed=embed(key, self.ctx, **kwargs))

    async def stop(self, key, **kwargs):
        await self.update(key, clear=True, **kwargs)

    async def time_out(self, key, secs, **kwargs):
        await self.update(key, clear=True, timeout=long_delta(timedelta(seconds=secs)), **kwargs)

    async def update(self, key, clear=False, **kwargs):
        if clear:
            await self.message.clear_reactions()

        self.last_key = key
        self.last_kwargs = kwargs

        await self.message.edit(embed=embed(key, self.ctx, **kwargs))

    async def refresh(self, **kwargs):
        self.last_kwargs.update(kwargs)
        await self.update(self.last_key, **self.last_kwargs)

    async def placeholder(self):
        await self.message.clear_reactions()
        await self.update("placeholder")


class Options(object):
    def __init__(self, menu, *selection, timeout=180.0, check=None):
        self.menu = menu
        self.selection = selection
        self.timeout = timeout
        self.check = check or self.default_check

    def default_check(self, reaction, user):
        return (reaction.message.id == self.menu.message.id
                and user == self.menu.ctx.author
                and reaction.emoji.name in self.selection)

    async def serve(self):
        await self.menu.message.clear_reactions()

        for e in self.selection:
            await self.menu.message.add_reaction(get_emoji(e))

    async def response(self):
        await self.serve()

        try:
            reaction, user = await self.menu.bot.wait_for("reaction_add",
                                                          timeout=self.timeout,
                                                          check=self.check)

        except TimeoutError:
            await self.menu.time_out(self.timeout)

        else:
            if reaction.emoji.name == "exit":
                await self.menu.stop()
                return False

            else:
                return reaction.emoji.name


class NumberedOptions(Options):
    def __init__(self, menu, iterable, *selection, start=0, timeout=180.0, check=None):
        self.iterable = iterable
        self.base_selection = list(selection)
        self._selection = []
        self._lastselection = []
        self.start = start
        self._page = 0
        self.max_page = len(iterable)//9 + 1
        self.write_pages()
        self._number = 0
        self._nlist = ""

        super().__init__(menu, timeout=timeout, check=check)

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = max(0, min(value, self.max_page-1))

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = value
        self._nlist = "".join((str(i) for i in range(1, value+1)))
    
    @property
    def nlist(self):
        return self._nlist

    @property
    def selection(self):
        return self._selection
    
    @selection.setter
    def selection(self, value):
        self.lastselection = self.selection
        self._selection = value

    def set_selection(self):
        s = self.base_selection.copy()
        self.number = len(self.pages[self.page])
        num_start = self.start
        
        if len(self.pages) > 1:
            if self.page != 0:
                s.insert(self.start, "pageback")
                num_start += 1

            if self.page != self.max_page - 1:
                s.insert(num_start, "pagenext")

        for i in range(self.number):
            s.insert(i+num_start, f"option{i+1}")

        self.selection = s

    def write_pages(self):
        self.pages = [{} for i in range(self.max_page)]

        for i, obj in enumerate(self.iterable):
            self.pages[i//9].update({str((i%9)+1): obj})
    

    async def response(self):
        self.set_selection()

        if len(self.selection) != len(self.lastselection):
            await self.serve()

        try:
            reaction, user = await self.menu.bot.wait_for("reaction_add",
                                                          timeout=self.timeout,
                                                          check=self.check)

        except TimeoutError:
            await self.menu.time_out(self.timeout)

        else:
            if reaction.emoji.name == "exit":
                await self.menu.stop()
                return False

            elif reaction.emoji.name == "pageback":
                self.page -= 1
                await self.menu.refresh(page=str(self), value=repr(self))
                await self.menu.message.remove_reaction(reaction, self.menu.ctx.author)
                return await self.response()

            elif reaction.emoji.name == "pagenext":
                self.page += 1
                await self.menu.refresh(page=str(self), value=repr(self))
                await self.menu.message.remove_reaction(reaction, self.menu.ctx.author)
                return await self.response()

            else:
                return reaction.emoji.name

    def option_n(self, n):
        return self.pages[self.page][n]

    def __str__(self):
        return f"Page {self.page+1} of {self.max_page}"

    def __repr__(self):
        return "\n".join([f"{mention_emoji(f'option{k}')}  {v}" for k, v in self.pages[self.page].items()])
