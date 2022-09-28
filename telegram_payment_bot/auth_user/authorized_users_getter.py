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
from telegram_payment_bot.config.configurable_object import ConfigurableObject
from telegram_payment_bot.misc.chat_members import ChatMembersGetter, ChatMembersList


#
# Classes
#

# Authorized users getter class
class AuthorizedUsersGetter:

    config: ConfigurableObject
    chat_members_getter: ChatMembersGetter

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigurableObject) -> None:
        self.config = config
        self.chat_members_getter = ChatMembersGetter(client)

    # Get authorized users
    def GetUsers(self,
                 chat: pyrogram.types.Chat) -> ChatMembersList:
        return self.chat_members_getter.FilterMembers(
            chat,
            lambda member: (
                member.user is not None and
                member.user.username is not None and
                member.user.username in self.config.GetValue(BotConfigTypes.AUTHORIZED_USERS)
            )
        )
