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

from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.misc.chat_members import ChatMembersGetter, ChatMembersList
from telegram_payment_bot.misc.helpers import MemberHelper


class MembersUsernameGetter:
    """Getter for chat members based on username criteria."""

    client: pyrogram.Client
    config: ConfigObject

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject) -> None:
        """Initialize the members username getter.

        Args:
            client: Pyrogram client instance
            config: Configuration object
        """
        self.client = client
        self.config = config

    async def GetAllWithUsername(self,
                                 chat: pyrogram.types.Chat) -> ChatMembersList:
        """Get all valid members that have a username.

        Args:
            chat: Chat to get members from

        Returns:
            List of chat members with usernames
        """
        return await ChatMembersGetter(self.client).FilterMembers(
            chat,
            lambda member: (
                MemberHelper.IsValidMember(member) and
                member.user is not None and
                member.user.username is not None
            )
        )

    async def GetAllWithNoUsername(self,
                                   chat: pyrogram.types.Chat) -> ChatMembersList:
        """Get all valid members that do not have a username.

        Args:
            chat: Chat to get members from

        Returns:
            List of chat members without usernames
        """
        return await ChatMembersGetter(self.client).FilterMembers(
            chat,
            lambda member: (
                MemberHelper.IsValidMember(member) and
                member.user is not None and
                member.user.username is None
            )
        )
