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
from __future__ import annotations

from typing import Union

import pyrogram

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.utils.utils import Utils


#
# Classes
#

# User class
class User:

    user: Union[int, str]

    # Construct from string
    @classmethod
    def FromString(cls,
                   config: ConfigObject,
                   user_str: str) -> User:
        if config.GetValue(BotConfigTypes.PAYMENT_USE_USER_ID):
            try:
                user = Utils.StrToInt(user_str)
            except ValueError:
                # Try also from float (it may happen in Excel files)
                try:
                    user = int(Utils.StrToFloat(user_str))
                except ValueError:
                    user = 0
            return cls(user)
        return cls(user_str[1:] if user_str.startswith("@") else user_str)

    # Construct from user object
    @classmethod
    def FromUserObject(cls,
                       config: ConfigObject,
                       user: pyrogram.types.User) -> User:
        if config.GetValue(BotConfigTypes.PAYMENT_USE_USER_ID):
            return cls(user.id)

        if user.username is None:
            raise ValueError("Class cannot be created from a None username")
        return cls(user.username)

    # Constructor
    def __init__(self,
                 user: Union[int, str]) -> None:
        self.user = user

    # Get if user ID
    def IsUserId(self) -> bool:
        return isinstance(self.user, int)

    # Get if username
    def IsUsername(self) -> bool:
        return isinstance(self.user, str) or self.user is None

    # Get if valid
    def IsValid(self) -> bool:
        return self.user != "" if self.IsUsername() else self.user != 0

    # Get value
    def Get(self) -> Union[int, str]:
        return self.user

    # Get as key
    def GetAsKey(self) -> Union[int, str]:
        if not self.IsValid():
            raise KeyError("An invalid user cannot be used as a key")

        return self.user if self.IsUserId() else self.user.lower()  # type: ignore

    # Convert to string
    def ToString(self) -> str:
        return f"{self.user}"

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()
