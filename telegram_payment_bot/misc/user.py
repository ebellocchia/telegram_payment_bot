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

from __future__ import annotations

from typing import Union

import pyrogram

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.utils.utils import Utils


class User:
    """Represents a user by either user ID or username."""

    user: Union[int, str]

    @classmethod
    def FromString(cls,
                   config: ConfigObject,
                   user_str: str) -> User:
        """
        Construct a User instance from a string representation.

        Args:
            config: The configuration object
            user_str: The string representation of the user (ID or username)

        Returns:
            A new User instance
        """
        if config.GetValue(BotConfigTypes.PAYMENT_USE_USER_ID):
            try:
                user = Utils.StrToInt(user_str)
            except ValueError:
                try:
                    user = int(Utils.StrToFloat(user_str))
                except ValueError:
                    user = 0
            return cls(user)
        return cls(user_str[1:] if user_str.startswith("@") else user_str)

    @classmethod
    def FromUserObject(cls,
                       config: ConfigObject,
                       user: pyrogram.types.User) -> User:
        """
        Construct a User instance from a Pyrogram User object.

        Args:
            config: The configuration object
            user: The Pyrogram User object

        Returns:
            A new User instance

        Raises:
            ValueError: If username is None when username mode is enabled
        """
        if config.GetValue(BotConfigTypes.PAYMENT_USE_USER_ID):
            return cls(user.id)

        if user.username is None:
            raise ValueError("Class cannot be created from a None username")
        return cls(user.username)

    def __init__(self,
                 user: Union[int, str]) -> None:
        """
        Initialize a User instance.

        Args:
            user: The user ID (int) or username (str)
        """
        self.user = user

    def IsUserId(self) -> bool:
        """
        Check if the user is represented by an ID.

        Returns:
            True if the user is represented by an ID, False otherwise
        """
        return isinstance(self.user, int)

    def IsUsername(self) -> bool:
        """
        Check if the user is represented by a username.

        Returns:
            True if the user is represented by a username, False otherwise
        """
        return isinstance(self.user, str) or self.user is None

    def IsValid(self) -> bool:
        """
        Check if the user representation is valid.

        Returns:
            True if the user is valid (non-empty username or non-zero ID), False otherwise
        """
        return self.user != "" if self.IsUsername() else self.user != 0

    def Get(self) -> Union[int, str]:
        """
        Get the user value (ID or username).

        Returns:
            The user ID or username
        """
        return self.user

    def GetAsKey(self) -> Union[int, str]:
        """
        Get the user value as a key for dictionary lookups.

        Returns:
            The user ID or lowercase username for consistent key lookups

        Raises:
            KeyError: If the user is invalid
        """
        if not self.IsValid():
            raise KeyError("An invalid user cannot be used as a key")

        return self.user if self.IsUserId() else self.user.lower()  # type: ignore

    def ToString(self) -> str:
        """
        Convert the user to a string representation.

        Returns:
            The string representation of the user
        """
        return f"{self.user}"

    def __str__(self) -> str:
        """
        Convert the user to a string representation.

        Returns:
            The string representation of the user
        """
        return self.ToString()
