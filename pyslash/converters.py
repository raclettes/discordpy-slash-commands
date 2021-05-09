from typing import Any, Callable, Dict, Union
import discord

from discord.ext import commands
from discord.ext.commands.errors import BadArgument
from discord_slash import SlashContext


class BadSlashArgument(commands.BadArgument):
    """
    Exception class for bad slash arguments. Raised by `handle_arg` and
    consequently `convert`.

    .. note::
        You should not raise this manually. This should be distinct to the
        converters.
    """
    pass


async def handle_arg(
    ctx: SlashContext,
    key: str,
    value: Any,
    type_: Union[Callable, commands.Converter]
) -> Any:
    """
    Handle an argument and deal with typing.Optional modifiers

    Parameters
    ----------
    ctx : SlashContext
        The context of the argument
    key : str
        The argument name
    value : any
        The value of the argument
    type_ : callable or commands.Converter
        The type, instance of type converter or type converter class

    Returns
    -------
    any
        The handled argument

    Raises
    ------
    BadSlashArgument
        Invalid argument, this occurs when no converter is able to provide a
        non-None response or not raise an error while converting. If a
        typing.Optional is provided, or any object with .__args__ containing
        NoneType, then this method will never raise and will instead return
        None.
    """
    # Is a typing.Optional, typing.Union, etc class
    if hasattr(type_, "__args__"):
        optional = type(None) in type_.__args__
        for item in type_.__args__:  # Iterate through possible types
            if item is None:
                # Don't try to convert with None
                continue

            try:
                # Attempt to convert, this also allows nesting of
                # typing.Optional etc
                new_value = await handle_arg(ctx, key, value, item)

                # Return by default if it's good (should go left to right)
                return new_value
            except Exception as exc:
                # This is optional, so we can skip past it
                pass
        
        if not optional:
            raise BadSlashArgument(message=f"Argument {key} is not of any valid type")
        
        return None
    else:
        if hasattr(type_, "convert"):
            # Check item is instantiated
            if isinstance(type_, type):
                # Instantaniate the class first
                type_converter = type_().convert
            else:
                # Grab the function of the init'd converter
                type_converter = type_.convert
            try:
                return await type_converter(ctx, value)
            except Exception as exc:
                raise BadSlashArgument(f"Failed to convert argument {key}") from exc
        else:
            # Probably not a converter
            return type_(value)
    

def convert(send_on_raise: bool = False, **converters: Dict[str, commands.Converter]):
    """
    Wraps slash commands to perform extra conversions on functions where
    necessary. Uses the same interface as the default command
    converter.

    .. note::
        This should only be used if you really really want to use the old
        slash interface. Otherwise, it's better to just use the decorators
        provided.
    
    Parameters
    ----------
    send_on_raise : bool
        Whether to send an epheremal message with the error message on failure,
        by default False
    **converters : Dict[str, commands.Converter]
        Converters where the name = Converter
    
    """
    def decorator(function):
        async def wrapper(self_or_ctx, *args, **kwargs):
            ctx = self_or_ctx if isinstance(self_or_ctx, SlashContext) else args[0]
            for key, type_ in converters.items():
                # If they're not a string, chances are they've already been
                # converted (member, int, etc)
                if type(kwargs.get(key)) != str:
                    continue
                
                try:
                    kwargs[key] = await handle_arg(ctx, key, kwargs.get(key), type_)
                except BadArgument as exc:
                    if send_on_raise:
                        await ctx.send(str(exc), hidden=True)
                    raise exc

            await function(self_or_ctx, *args, **kwargs)
        wrapper.__annotations__ = function.__annotations__
        return wrapper
    return decorator
