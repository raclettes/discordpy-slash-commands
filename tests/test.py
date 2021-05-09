import unittest
from typing import Literal, Optional, Union

from discord.ext import commands
from discord_slash.model import SlashCommandOptionType
from pyslash.decorators import (get_slash_command_type, get_slash_kwargs,
                                is_optional_of)
from pyslash.utils import is_converter, validate_literal_union


class TestPySlash(unittest.TestCase):
    def test_literal_list(self):
        self.assertTrue(
            validate_literal_union(Union[Literal[1, "name"], Literal[2, "test"]]))

    def test_bad_literal_list(self):
        self.assertFalse(
            validate_literal_union(Union[Literal[1, "name"], Literal["incorrect", "test"]]))

    def test_converter_checks(self):
        self.assertTrue(
            is_converter(commands.Converter()))
        self.assertTrue(
            is_converter(commands.Converter))

    def test_optional_checks(self):
        self.assertTrue(
            is_optional_of(Optional[commands.Converter], commands.Converter))
        self.assertTrue(
            is_optional_of(Union[commands.Converter, str], commands.Converter))

    def test_param_type(self):
        self.assertEqual(
            get_slash_command_type(commands.Converter), SlashCommandOptionType.STRING)
        self.assertEqual(
            get_slash_command_type(Optional[commands.Converter]), SlashCommandOptionType.STRING)
        self.assertEqual(
            get_slash_command_type(Union[commands.Converter, str]), SlashCommandOptionType.STRING)

    def test_slash_kwarg_generation(self):
        def func(foo: str, bar: Union[Literal[1], Literal[2, "name"]], baz: Union[commands.Converter, int] = "bin"):
            pass

        kwargs, _ = get_slash_kwargs("test", "test", [], False, func)
        self.assertEqual(kwargs["options"][0], {
            "name": "foo",
            "description": "No description",
            "type": SlashCommandOptionType.STRING,
            "required": True,
            "choices": []
        })

        self.assertEqual(kwargs["options"][1], {
            "name": "bar",
            "description": "No description",
            "type": SlashCommandOptionType.INTEGER,
            "required": True,
            "choices": [
                {"name": "1", "value": 1},
                {"name": "name", "value": 2}
            ]
        })

        self.assertEqual(kwargs["options"][2], {
            "name": "baz",
            "description": "No description",
            "type": SlashCommandOptionType.STRING,
            "required": False,
            "choices": []
        })
    
    def test_optional_converter(self):
        def func(baz: Optional[commands.Converter] = "bin"):
            pass

        kwargs, _ = get_slash_kwargs("test", "test", [], False, func)
        self.assertEqual(kwargs["options"][0], {
            "name": "baz",
            "description": "No description",
            "type": SlashCommandOptionType.STRING,
            "required": False,
            "choices": []
        })


if __name__ == "__main__":
    unittest.main()
