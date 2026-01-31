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
from telegram_payment_bot.misc.chat_members import ChatMembersGetter, ChatMembersList


class AuthorizedUsersGetter:
    """Getter for authorized users from a chat."""

    config: ConfigObject
    chat_members_getter: ChatMembersGetter

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject) -> None:
        """
        Constructor.

        Args:
            client: Pyrogram client
            config: Configuration object
        """
        self.config = config
        self.chat_members_getter = ChatMembersGetter(client)

    async def GetUsers(self,
                       chat: pyrogram.types.Chat) -> ChatMembersList:
        """
        Get all authorized users from the specified chat.

        Args:
            chat: Telegram chat

        Returns:
            List of authorized chat members
        """
        return await self.chat_members_getter.FilterMembers(
            chat,
            lambda member: (
                member.user is not None
                and member.user.username is not None
                and member.user.username in self.config.GetValue(BotConfigTypes.AUTHORIZED_USERS)
            ),
        )
