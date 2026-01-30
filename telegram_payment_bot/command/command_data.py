# Copyright (c) 2026 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import Any, Callable, Optional, Union

import pyrogram

from telegram_payment_bot.utils.utils import Utils
from telegram_payment_bot.utils.wrapped_list import WrappedList


class CommandParameterError(Exception):
    """Exception raised for command parameter errors."""


class CommandParametersList(WrappedList):
    """List of command parameters."""

    def GetAsBool(self,
                  idx: int,
                  def_val: Optional[bool] = None) -> bool:
        """
        Get parameter as boolean.

        Args:
            idx: Parameter index
            def_val: Default value if parameter not found

        Returns:
            Parameter value as boolean
        """
        return self.__GetGenericParam(Utils.StrToBool, idx, def_val)

    def GetAsInt(self,
                 idx: int,
                 def_val: Optional[int] = None) -> int:
        """
        Get parameter as integer.

        Args:
            idx: Parameter index
            def_val: Default value if parameter not found

        Returns:
            Parameter value as integer
        """
        return self.__GetGenericParam(Utils.StrToInt, idx, def_val)

    def GetAsString(self,
                    idx: int,
                    def_val: Optional[str] = None) -> str:
        """
        Get parameter as string.

        Args:
            idx: Parameter index
            def_val: Default value if parameter not found

        Returns:
            Parameter value as string
        """
        return self.__GetGenericParam(str, idx, def_val)

    def IsLast(self,
               value: Union[int, str]) -> bool:
        """
        Check if last parameter is the specified value.

        Args:
            value: Value to check

        Returns:
            True if value is the last parameter, False otherwise
        """
        try:
            return value == self.list_elements[self.Count() - 1]
        except IndexError:
            return False

    def IsValue(self,
                value: Union[int, str]) -> bool:
        """
        Check if value is present in parameters.

        Args:
            value: Value to check

        Returns:
            True if value is present, False otherwise
        """
        return value in self.list_elements

    def __GetGenericParam(self,
                          conv_fct: Callable[[str], Any],
                          idx: int,
                          def_val: Optional[Any]) -> Any:
        """
        Get generic parameter with conversion function.

        Args:
            conv_fct: Conversion function to apply
            idx: Parameter index
            def_val: Default value if parameter not found

        Returns:
            Converted parameter value

        Raises:
            CommandParameterError: If parameter is invalid and no default value provided
        """
        try:
            return conv_fct(self.list_elements[idx])
        except (ValueError, IndexError) as ex:
            if def_val is not None:
                return def_val
            raise CommandParameterError(f"Invalid command parameter #{idx}") from ex


class CommandData:
    """Data extracted from a command message."""

    cmd_name: str
    cmd_params: CommandParametersList
    cmd_chat: pyrogram.types.Chat
    cmd_user: Optional[pyrogram.types.User]

    def __init__(self,
                 message: pyrogram.types.Message) -> None:
        """
        Constructor.

        Args:
            message: Telegram message containing the command

        Raises:
            ValueError: If message is not a valid command
        """
        if message.command is None or message.chat is None:
            raise ValueError("Invalid command")

        self.cmd_name = message.command[0]
        self.cmd_params = CommandParametersList()
        self.cmd_params.AddMultiple(message.command[1:])
        self.cmd_chat = message.chat
        self.cmd_user = message.from_user

    def Name(self) -> str:
        """
        Get command name.

        Returns:
            Command name
        """
        return self.cmd_name

    def Chat(self) -> pyrogram.types.Chat:
        """
        Get command chat.

        Returns:
            Telegram chat where command was executed
        """
        return self.cmd_chat

    def User(self) -> Optional[pyrogram.types.User]:
        """
        Get command user.

        Returns:
            User who executed the command, None if anonymous
        """
        return self.cmd_user

    def Params(self) -> CommandParametersList:
        """
        Get command parameters.

        Returns:
            List of command parameters
        """
        return self.cmd_params
