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

from datetime import datetime, timedelta

import pyrogram


class BanHelperConst:
    """Constants for ban helper class."""

    BAN_TIME_SEC: int = 60


class BanHelper:
    """Helper class for banning, kicking, and unbanning users from chats."""

    client: pyrogram.Client

    def __init__(self,
                 client: pyrogram.Client) -> None:
        """
        Initialize the ban helper.

        Args:
            client: The Pyrogram client instance
        """
        self.client = client

    async def BanUser(self,
                      chat: pyrogram.types.Chat,
                      user: pyrogram.types.User) -> None:
        """
        Ban a user from a chat permanently.

        Args:
            chat: The chat to ban the user from
            user: The user to ban
        """
        await self.client.ban_chat_member(chat.id,
                                          user.id,
                                          until_date=datetime.now())

    async def KickUser(self,
                       chat: pyrogram.types.Chat,
                       user: pyrogram.types.User) -> None:
        """
        Kick a user from a chat temporarily.

        Args:
            chat: The chat to kick the user from
            user: The user to kick
        """
        await self.client.ban_chat_member(chat.id,
                                          user.id,
                                          until_date=datetime.now() + timedelta(seconds=BanHelperConst.BAN_TIME_SEC))

    async def UnbanUser(self,
                        chat: pyrogram.types.Chat,
                        user: pyrogram.types.User) -> None:
        """
        Unban a user from a chat.

        Args:
            chat: The chat to unban the user from
            user: The user to unban
        """
        await self.client.unban_chat_member(chat.id, user.id)
