from os import getenv
from typing import Literal, Tuple
import discord

from discord_slash.context import SlashContext
from pyslash import slash

from discord.ext import commands
from discord.flags import Intents
from discord_slash import SlashCommand
from dotenv import load_dotenv
load_dotenv()

guild_ids = []
guild_id = getenv("GUILD_ID")
if guild_id:
    guild_ids = [int(guild_id)]

bot = commands.Bot(command_prefix="!", intents=Intents.all())
s = SlashCommand(bot, sync_commands=True)


@slash(s, description="Test", guild_ids=guild_ids)
async def echo(ctx: SlashContext, my_arg: Tuple[str, Literal["a description"]]):
    await ctx.send(f"You said {my_arg}")

@slash(s, name="test", guild_ids=guild_ids)
async def _test(ctx: SlashContext, member: discord.Member):
    await ctx.send(f"Hello {member.mention}")


bot.run(getenv("BOT_TOKEN"))
