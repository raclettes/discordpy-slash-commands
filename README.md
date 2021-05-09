# Pyslash
Pyslash is a wrapper around [discord-py-slash-command](https://github.com/eunwoo1104/discord-py-slash-command), that makes command creation more natural.

The examples provided are based of the examples from the original repository.

## Quick startup
Firstly you must install the package, as explained [here](#installation).

A simple setup using `slash` and adding a basic command.
```python
import discord
from discord.ext import commands
from pyslash import SlashCommand, SlashContext

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
s = SlashCommand(bot)

@s.slash(name="test")
async def _test(ctx: SlashContext, arg0: str):
    embed = discord.Embed(title="embed test")
    await ctx.send(content=arg0, embeds=[embed])

bot.run("discord_token")
```
*As of `1.1.0`, you no longer need to import `slash` from `pyslash` and provide the instance as the first variable, as pyslash now has a subclass of `SlashCommand` that does this for you.*

Converters are automatically handled, for example
```python
@s.slash(name="test")
async def _test(ctx: SlashContext, member: discord.Member):
    await ctx.send(f"*taps mic* testing, {member.mention}")
```

And names don't have to be given
```python
@s.slash()
async def foo(ctx: SlashContext, member: discord.Member):
    # This command will automatically be called 'foo'
    await ctx.send(f"Hello, {member.mention}")
```

### Descriptions

By default, each argument and command has the description `No description`, but that can be changed by providing a docstring. Docstrings are supported as provided by [docstring-parser](https://pypi.org/project/docstring-parser/) &mdash; *at time of writing, that is [ReST](https://www.python.org/dev/peps/pep-0287/), [Google](https://google.github.io/styleguide/pyguide.html), and [Numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html).*
```python
from typing import Tuple, Literal

# ...

@s.slash()
async def foo(ctx: SlashContext, member: discord.Member):
    """
    My command description here!

    :param member: my description here
    """
    # This command will automatically be called 'foo', and have the description
    # "My command description here!", and the argument `member` will have the
    # description "my description here".
    await ctx.send(f"Hello, {member.mention}")
```

It's also possible to pass the command description through the decorator as follows, although that's not recommended (and will override any docstring provided description):
```python
@s.slash(description="My description!")
async def command(ctx):
    pass
```

## Advanced usage
The same usage applies for cogs, but a different function is used.

```python
# bot.py
from discord.ext import commands
from pyslash import SlashCommand

bot = commands.Bot(command_prefix="prefix")
slash = SlashCommand(bot, override_type = True)

bot.load_extension("cog")
bot.run("TOKEN")

# cog.py
import discord
from discord.ext import commands
from pyslash import SlashContext, slash_cog

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

To install from source, clone the repository and then build:
```
git clone https://github.com/starsflower/discordpy-slash-commands.git
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