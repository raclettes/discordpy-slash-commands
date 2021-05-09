# Pyslash
Pyslash is a wrapper around [discord-py-slash-command](https://github.com/eunwoo1104/discord-py-slash-command), that makes command creation more natural.

The examples provided are based of the examples from the original repository.

## Quick startup
Firstly you must install the package, as explained [here](#installation).

A simple setup using `slash` and adding a basic command
```python
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from pyslash import slash

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
s = SlashCommand(bot)

@slash(s, name="test")
async def _test(ctx: SlashContext, arg0: str):
    embed = discord.Embed(title="embed test")
    await ctx.send(content=arg0, embeds=[embed])

bot.run("discord_token")
```

Converters are automatically handled, for example
```python
@slash(s, name="test")
async def _test(ctx: SlashContext, member: discord.Member):
    await ctx.send(f"*taps mic* testing, {member.mention}")
```

And names don't have to be given
```python
@slash(s)
async def foo(ctx: SlashContext, member: discord.Member):
    # This command will automatically be called 'foo'
    await ctx.send(f"Hello, {member.mention}")
```

### Descriptions

By default, each argument has the description `No description`, but that can be changed by providing a `Tuple` of any type and a `Literal`.
```python
from typing import Tuple, Literal

# ...

description = Literal["my description here"]
@slash(s)
async def foo(ctx: SlashContext, member: typing.Tuple[discord.Member, description]):
    # This command will automatically be called 'foo', and have
    # the description "my description here"
    await ctx.send(f"Hello, {member.mention}")
```

## Advanced usage
The same usage applies for cogs, but a different function is used.

```python
# bot.py
from discord.ext import commands
from discord_slash import SlashCommand

bot = commands.Bot(command_prefix="prefix")
slash = SlashCommand(bot, override_type = True)

bot.load_extension("cog")
bot.run("TOKEN")

# cog.py
import discord
from discord.ext import commands
from discord_slash import SlashContext
from pyslash import cog_ext

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_cog(name="test")
    async def _test(self, ctx: SlashContext):
        await ctx.send("Hey there folks")

def setup(bot):
    bot.add_cog(Slash(bot))
```

## Installation
To install from pip, run
```
pip install dpyslash
```

To install, clone the repository and then build:
```
git clone https://github.com/starsflower/discordpy-slash-commands
cd discordpy-slash-commands
python setup.py install
```

## Tests
To run basic tests, run
```
python -m tests/test
```

To run the test bot (that requires `BOT_TOKEN` in the environment variables), and a further pip requirement of `python-dotenv`
```
python -m tests/test_bot
```