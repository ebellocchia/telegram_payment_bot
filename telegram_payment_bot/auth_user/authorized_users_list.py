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

import pyrogram

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.utils.wrapped_list import WrappedList


class AuthorizedUsersList(WrappedList):
    """List of authorized users."""

    def __init__(self,
                 config: ConfigObject) -> None:
        """
        Constructor.

        Args:
            config: Configuration object
        """
        super().__init__()
        self.AddMultiple(config.GetValue(BotConfigTypes.AUTHORIZED_USERS))

    def IsUserPresent(self,
                      user: pyrogram.types.User) -> bool:
        """
        Check if a user is present in the authorized users list.

        Args:
            user: Pyrogram user

        Returns:
            True if user is present, False otherwise
        """
        return user.username is not None and user.username in self.list_elements

    def ToString(self) -> str:
        """
        Convert the authorized users list to a formatted string.

        Returns:
            String with usernames formatted as list items
        """
        return "\n".join([f"- @{username}" for username in self.list_elements])

    def __str__(self) -> str:
        """
        Convert the authorized users list to a string.

        Returns:
            String representation of the list
        """
        return self.ToString()
