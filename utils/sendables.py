from datetime import datetime
from json import load

from discord import Embed

from bot import bot
from utils import on_vps, match_files
from utils.emoji import mention_emoji

DEFAULT_COLOUR = 0x8d2f2f
ERROR_ICON = "https://cdn.discordapp.com/attachments/710177462989881415/710866387018711080/cancel.png"
INFO_ICON = "https://cdn.discordapp.com/attachments/710177462989881415/711348122915176529/info.png"


def load_json(fn):
	with open(f"./data/{fn}.json", "r", encoding="utf-8") as jf:
		return load(jf)


MESSAGES = load_json("messages")
SUCCESS_MESSAGES = load_json("success_messages")
ERROR_MESSAGES = load_json("error_messages")
INFO_MESSAGES = load_json("info_messages")
EMBEDS = {}
for file in match_files("./data/*_embeds.json"):
	EMBEDS.update(load_json(file))


def message(key, **kwargs):
	return MESSAGES[key].format(p="&", **kwargs)


def errmsg(key, **kwargs):
	return f"{mention_emoji('cancel')}  {ERROR_MESSAGES[key].format(p='&', **kwargs)}"


def infmsg(key, **kwargs):
	return f"{mention_emoji('info')}  {INFO_MESSAGES[key].format(p='&', **kwargs)}"


def sucmsg(key, **kwargs):
	return f"{mention_emoji('confirm')}  {SUCCESS_MESSAGES[key].format(p='&', **kwargs)}"	


def embed(key, ctx=None, *, user=None, guild=None, colour=None, thumbnail=None, icon=None, image=None, fields={}, **kwargs):
	def f(text):
		return text.format(p=">>", **kwargs)

	e = EMBEDS[key]

	header_text = e["header"] if "header" in e.keys() else "Source"
	title = f(e["title"]) if "title" in e.keys() else ""
	description = f(e["desc"]) if "desc" in e.keys() else ""
	footer_text = e["footer"] if "footer" in e.keys() else f"Requested by {ctx.author.display_name}" if ctx else None
	footer_icon = ctx.author.avatar_url if ctx else None
	fields = e["fields"] if "fields" in e.keys() else fields
	colour = (colour
			  or e["colour"] if "colour" in e.keys() else None
			  or ctx.author.colour if ctx and ctx.author.colour.value else None
			  or DEFAULT_COLOUR)
	thumbnail = (thumbnail
				 or e["thumbnail"] if "thumbnail" in e.keys() else None
				 or bot.user.avatar_url if icon == "bot" else None
				 or ctx.author.avatar_url if icon == "author" else None
				 or ctx.guild.icon_url if icon == "origin" else None
				 or guild.icon_url if icon == "guild" else None
				 or user.avatar_url if icon == "user" else None
				 or INFO_ICON if icon == "info" else None
				 or ERROR_ICON if icon == "error" else None)
	image = e["image"] if "image" in e.keys() else image

	embed = Embed(title=title, description=description, colour=colour, timestamp=datetime.utcnow())
	embed.set_author(name=header_text)
	if footer_icon:
		embed.set_footer(text=footer_text, icon_url=footer_icon)
	if thumbnail:
		embed.set_thumbnail(url=thumbnail)
	if image:
		embed.set_image(url=image)

	for n, v in fields.items():
		null = n == "null"
		name = "\u200b" if null else f(n)
		value = "\u200b" if null else f(v["value"])
		inline = True if null else v["inline"] if "inline" in v.keys() else False

		embed.add_field(name=name, value=value, inline=inline)

	return embed