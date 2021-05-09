from typing import List
from discord_slash import SlashCommand as SlashCommandOriginal

from .decorators import slash


class SlashCommand(SlashCommandOriginal):
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
        remove_underscore_keywords : bool, optional
            Whether to remove _ from the end of arguments that would be keywords,
            by default True
        """
        return slash(
            slash_class=super(),
            name=name,
            description=description,
            guild_ids=guild_ids,
            remove_underscore_keywords=remove_underscore_keywords
        )
