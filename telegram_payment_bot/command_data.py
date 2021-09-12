# Copyright (c) 2021 Emanuele Bellocchia
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

#
# Imports
#
import pyrogram
from typing import Union
from telegram_payment_bot.utils import Utils
from telegram_payment_bot.wrapped_list import WrappedList


#
# Classes
#

# Command parameters list class
class CommandParametersList(WrappedList):
    # Get parameter as bool
    def GetAsBool(self,
                  idx: int) -> bool:
        try:
            return Utils.StrToBool(self.list_elements[idx])
        except (ValueError, IndexError):
            return False

    # Get parameter as int
    def GetAsInt(self,
                 idx: int) -> int:
        try:
            return int(self.list_elements[idx])
        except (ValueError, IndexError):
            return 0

    # Get parameter as string
    def GetAsString(self,
                    idx: int) -> str:
        try:
            return str(self.list_elements[idx])
        except (ValueError, IndexError):
            return ""

    # Check if last parameter is the specified value
    def IsLast(self,
               value: Union[int, str]) -> bool:
        try:
            return value == self.list_elements[self.Count() - 1]
        except IndexError:
            return False

    # Check if value is present
    def IsValue(self,
                value: Union[int, str]) -> bool:
        return value in self.list_elements


# Command data
class CommandData:
    def __init__(self,
                 message: pyrogram.types.Message) -> None:
        self.cmd_name = message.command[0]
        self.cmd_params = CommandParametersList()
        self.cmd_params.AddMultiple(message.command[1:])
        self.cmd_chat = message.chat
        self.cmd_user = message.from_user

    # Get name
    def Name(self) -> str:
        return self.cmd_name

    # Get chat
    def Chat(self) -> pyrogram.types.Chat:
        return self.cmd_chat

    # Get user
    def User(self) -> pyrogram.types.User:
        return self.cmd_user

    # Get parameters
    def Params(self) -> CommandParametersList:
        return self.cmd_params
