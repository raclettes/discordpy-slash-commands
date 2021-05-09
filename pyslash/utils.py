import inspect
import keyword
from typing import Any, List, Literal, Union

from discord.ext import commands
from discord.ext.commands.errors import CommandError
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option


class InvalidParameter(CommandError):
    pass


def is_converter(value: Any) -> bool:
    return (isinstance(value, type) and issubclass(value, commands.Converter)) \
        or isinstance(value, commands.Converter)


def is_optional_of(value: Any, i: Any):
    """
    See if `value` is a subclass of `i` hidden by `typing.Optional` or
    `typing.Union`

    Parameters
    ----------
    value : Any
        The potential class
    i : Any
        The class to check against
    """
    return get_root_type(value) == i


def get_root_type(value: Any):
    """
    Gets the root type of an annotation naively

    Parameters
    ----------
    value : Any
        The annotation to check

    Returns
    -------
    type
        A type
    """
    if hasattr(value, "__args__"):
        return get_root_type(value.__args__[0])

    if isinstance(value, type):
        return value
    else:
        return type(value)


def validate_literal_union(union: Any) -> bool:
    """
    Validate a Union parameter. All arguments must be a literal and
    of the same type. This only includes the first parameter

    Parameters
    ----------
    union : Union
        The Union to check

    Returns
    -------
    bool
        Whether it's valid
    """
    if not hasattr(union, "__args__"):
        return False

    are_all_literals = all(getattr(arg, "__origin__", None)
                           == Literal for arg in union.__args__)

    if are_all_literals:
        are_all_same_type = len(
            set(type(arg.__args__[0]) for arg in union.__args__)) == 1
        return are_all_same_type

    return False


def get_slash_command_type(annotation: Any) -> SlashCommandOptionType:
    """
    Get slash command type from an annotation. This considers optionals and
    converters

    Parameters
    ----------
    annotation : Any
        Annotation to check

    Returns
    -------
    SlashCommandOptionType
        The parameter type

    Raises
    ------
    InvalidParameter
        No parameter type could be found
    """
    # If it's a converter or an optional of a converter, it will always be a string
    if get_root_type(annotation) == commands.Converter:
        return SlashCommandOptionType.STRING

    type_ = SlashCommandOptionType.from_type(get_root_type(annotation))
    if type_ is None:
        raise InvalidParameter(
            f"Parameter: {str(annotation)} does not match any Discord type")

    return type_


def get_slash_kwargs(name: str, description: str, guild_ids: List[int], remove_underscore_keywords: bool, function):
    """
    Get the kwargs required for cog_ext.cog_slash or SlashCommand.slash

    Parameters
    ----------
    name : str
        The name of the command
    description : str
        The description of the command
    guild_ids : List[int]
        List of guild IDs to add the command to
    remove_underscore_keywords : bool
        Whether to remove _ from the end of arguments that would be keywords
    function : any
        The command

    Returns
    -------
    dict
        The arguments as a kwarg
    dict
        The connectors for the parameter names
    """
    # Use annotations
    signature = inspect.signature(function)

    params = dict(
        name=name or function.__name__,
        description=description or "No description",
        guild_ids=guild_ids,
        options=[]
    )
    param_name_mapping = dict()
    converter_params = dict()

    for param_name, parameter in signature.parameters.items():
        annotation = parameter.annotation
        if annotation == SlashContext or param_name == "self":
            continue

        # If it's a keyword with an underscore, then remove the underscore
        # for Discord's sake
        if remove_underscore_keywords and keyword.iskeyword(param_name[:-1]):
            # def_ -> def, in_ -> in
            param_name_mapping[param_name[:-1]] = param_name
            param_name = param_name[:-1]

        # If it's a tuple of a type and a literal, the second argument is a description
        param_description = "No description"
        if getattr(annotation, "__origin__", None) == tuple and len(annotation.__args__) == 2:
            param_description = annotation.__args__[1].__args__[0]
            annotation = annotation.__args__[0]

        # Default to no choices
        choices = None
        # Unions of literals are considered choices, rather than converters
        if validate_literal_union(annotation):
            choices = []
            for literal in annotation.__args__:
                # Literal[1, "My naparam_nameme"] would give choice 1, of name Name
                choice_value = literal.__args__[0]
                if len(literal.__args__) > 1:
                    choice_name = literal.__args__[1]
                else:
                    choice_name = str(choice_value)
                choices.append(create_choice(choice_value, choice_name))
        else:
            # Just use converter params
            converter_params[param_name] = annotation

        params['options'].append(create_option(
            name=param_name,
            description=param_description,
            option_type=get_slash_command_type(annotation),
            required=parameter.default == inspect.Parameter.empty,
            choices=choices
        ))

    params['connector'] = param_name_mapping
    return params, converter_params
