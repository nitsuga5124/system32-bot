from discord.utils import get

from bot import bot


def get_emoji(name):
    hub = bot.get_cog("Hub")

    return get(hub.guild.emojis, name=name)


def get_emojis(*names):
    hub = bot.get_cog("Hub")

    return [get(hub.guild.emojis, name=name) for name in names]


def mention_emoji(name):
    return f"{str(get_emoji(name))}"
