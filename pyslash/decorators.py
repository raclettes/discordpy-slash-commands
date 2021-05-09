
from typing import List

from discord_slash import SlashCommand, cog_ext

from .converters import convert
from .utils import *


def slash_cog(name: str = None, description: str = None, guild_ids: List[int] = None, remove_underscore_keywords: bool = True):
    """
    Add a command to a cog

    Parameters
    ----------
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
    def decorator(function):
        # Use annotations
        params, converter_params = get_slash_kwargs(
            function, name, description, guild_ids, remove_underscore_keywords)
        return cog_ext.cog_slash(**params)(convert(**converter_params)(function))

    return decorator


def slash(slash_class: SlashCommand, name: str = None, description: str = None, guild_ids: List[int] = None, remove_underscore_keywords: bool = True):
    """
    Add a command to a bot at the top level

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
    def decorator(function):
        # Use annotations
        params, converter_params = get_slash_kwargs(
            function, name, description, guild_ids, remove_underscore_keywords)
        return slash_class.slash(**params)(convert(**converter_params)(function))

    return decorator
