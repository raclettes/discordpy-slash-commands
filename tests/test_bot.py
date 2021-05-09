from os import getenv
from typing import Literal, Tuple
import discord

from discord_slash.context import SlashContext
from pyslash import SlashCommand

from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
load_dotenv()

guild_ids = []
guild_id = getenv("GUILD_ID")
if guild_id:
    guild_ids = [int(guild_id)]

bot = commands.Bot(command_prefix="!", intents=Intents.all())
s = SlashCommand(bot, sync_commands=True)


@s.slash(description="Test", guild_ids=guild_ids)
async def echo(ctx: SlashContext, my_arg: Tuple[str, Literal["a description"]]):
    await ctx.send(f"You said {my_arg}")

@s.slash(name="test", guild_ids=guild_ids)
async def _test(ctx: SlashContext, member: discord.Member):
    await ctx.send(f"Hello {member.mention}")


bot.run(getenv("BOT_TOKEN"))
