from aiosqlite import connect

from utils import match_files


class AsyncDatabase(object):
    def __init__(self, bot):
        self.bot = bot
        self.path = "./data/database.db3"
        self.build_path = "./data/build.sql"

    async def connect(self):
        self.cxn = await connect(self.path)

    async def commit(self):
        await self.cxn.commit()

    async def close(self):
        await self.cxn.close()

    async def build(self):
        await self.executescript(self.build_path)

    async def field(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))

        if (row := await cur.fetchone()) is not None:
            return row[0]

    async def record(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))

        return await cur.fetchone()

    async def records(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))

        return await cur.fetchall()

    async def column(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))

        return [row[0] for row in await cur.fetchall()]

    async def execute(self, command, *values):
        await self.cxn.execute(command, tuple(values))

    async def executemany(self, command, valueset):
        await self.cxn.executemany(command, valueset)

    async def executescript(self, path, **kwargs):
        with open(path, "r", encoding="utf-8") as script:
            await self.cxn.executescript(script.read().format(**kwargs))


class Ready(object):
    def __init__(self):
        self.bot = False
        self.cogs = match_files("./cogs/*.py")

        for cog in self.cogs:
            setattr(self, cog, False)

    def up(self, cog):
        setattr(self, (qn := cog.qualified_name.lower()), True)
        print(f" {qn} cog ready")

    @property
    def all(self):
        return all([getattr(self, cog) for cog in self.cogs])
