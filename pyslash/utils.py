import inspect
import keyword
from typing import Any, Dict, List, Literal, Union

from discord.ext import commands
from discord.ext.commands.errors import CommandError
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from docstring_parser import parse
from docstring_parser.common import DocstringParam


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
    # If there's no annotation, assume it's a string
    if annotation == inspect.Parameter.empty:
        return SlashCommandOptionType.STRING
    
    root_type = get_root_type(annotation)

    # If it's a converter or an optional of a converter, it will always be a string
    if issubclass(root_type, commands.Converter):
        return SlashCommandOptionType.STRING

    # Otherwise, try to fetch from enum
    type_ = SlashCommandOptionType.from_type(root_type)
    if type_ is None:
        raise InvalidParameter(
            f"Parameter annotation {str(annotation)} does not match any Discord "
             "type (perhaps use a converter?)")

    return type_


def get_descriptions(params: List[DocstringParam]) -> Dict[str, str]:
    """
    Turn a list of docstring paramsinto a dictionary

    Parameters
    ----------
    params : List[DocstringParam]
        The docstring params

    Returns
    -------
    Dict[str, str]
        The dictionary of parameter: description
    """
    descriptions = {}
    for param in params:
        name, description = param.arg_name, param.description
        descriptions[name] = description

    return descriptions


def get_slash_kwargs(function: Any, name: str = None, description: str = None, guild_ids: List[int] = None, remove_underscore_keywords: bool = False):
    """
    Get the kwargs required for cog_ext.cog_slash or SlashCommand.slash

    Parameters
    ----------
    function : any
        The command
    name : str, optional
        The name of the command, by default None
    description : str, optional
        The description of the command (will override any docstring provided
        description if not None), by default None
    guild_ids : List[int], optional
        List of guild IDs to add the command to, by default None
    remove_underscore_keywords : bool, optional
        Whether to remove _ from the end of arguments that would be keywords,
        by default False

    Returns
    -------
    dict
        The arguments as a kwarg
    dict
        The connectors for the parameter names
    """
    # Use annotations
    signature = inspect.signature(function)
    # Use docstring signatures to get descriptions
    parsed_docstring = parse(function.__doc__)
    # Command description
    description = description or parsed_docstring.short_description
    # Parameter descriptions
    param_descriptions = get_descriptions(parsed_docstring.params)

    # Building params for function
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

        # Get descriptions or use default
        param_description = param_descriptions.get(
            param_name, "No description")

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

        # Add the parameter/"option"
        params['options'].append(create_option(
            name=param_name,
            description=param_description,
            option_type=get_slash_command_type(annotation),
            required=parameter.default == inspect.Parameter.empty,
            choices=choices
        ))

    params['connector'] = param_name_mapping
    return params, converter_params
