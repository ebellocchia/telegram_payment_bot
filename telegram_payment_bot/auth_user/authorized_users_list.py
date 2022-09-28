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

from telegram_payment_bot.bot.bot_config import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.utils.wrapped_list import WrappedList


#
# Classes
#

# Authorized users list class
class AuthorizedUsersList(WrappedList):
    # Constructor
    def __init__(self,
                 config: ConfigObject) -> None:
        super().__init__()
        self.AddMultiple(config.GetValue(BotConfigTypes.AUTHORIZED_USERS))

    # Get if a user is present
    def IsUserPresent(self,
                      user: pyrogram.types.User) -> bool:
        return user.username is not None and user.username in self.list_elements

    # Convert to string
    def ToString(self) -> str:
        return "\n".join([f"- @{username}" for username in self.list_elements])

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()
