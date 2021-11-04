from typing import List, Optional, Union
import discord
from discord.ext import commands
from discord_slash import SlashCommand as SlashCommandOriginal

from .decorators import slash


class SlashCommand(SlashCommandOriginal):
    def __init__(self, client: Union[discord.Client, commands.Bot], sync_commands: bool = False, delete_from_unused_guilds: bool = False, sync_on_cog_reload: bool = False, override_type: bool = False, application_id: Optional[int] = None, guild_ids: Optional[List[int]] = None):
        """
        Create a SlashCommand manager. As per normal usage, but contains the
        following extra parameter to allow general guild ID setting.

        .. note::
            Other information can be seen on the original
            `SlashCommand.__init__`.

        Parameters
        ----------
        guild_ids : Optional[List[int]], optional
            Default value for guild_ids for commands, by default None
        """
        super().__init__(client, sync_commands=sync_commands, delete_from_unused_guilds=delete_from_unused_guilds, sync_on_cog_reload=sync_on_cog_reload, override_type=override_type, application_id=application_id)

        # Set value (publicly accessible as it can be overridden later if
        # desired)
        self.guild_ids = guild_ids
    
    def slash(self, name: str = None, description: str = None, guild_ids: List[int] = None, remove_underscore_keywords: bool = True):
        """
        Add a command to a bot at the top level

        .. note::
            Unlike the original implementation of `SlashCommand.slash`, this
            doesn't require parameter definitions and also allows converters

        Parameters
        ----------
        slash_class : SlashCommand
            The slash object to add this command to
        name : str, optional
            The name of the command, by default None
        description : str, optional
            The description, by default None
        guild_ids : List[int], optional
            The guild IDs to add the command to, by default None

            If no value is provided, the value of `guild_ids` passed to
            `__init__` is used. If a value is provided, this takes precedence
            over the default value.
        remove_underscore_keywords : bool, optional
            Whether to remove _ from the end of arguments that would be keywords,
            by default True
        """
        return slash(
            slash_class=super(),
            name=name,
            description=description,
            guild_ids=guild_ids or self.guild_ids,
            remove_underscore_keywords=remove_underscore_keywords
        )
