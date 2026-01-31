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

from typing import Callable, Optional

import pyrogram
from pyrogram.enums import ChatMembersFilter

from telegram_payment_bot.misc.helpers import UserHelper
from telegram_payment_bot.utils.wrapped_list import WrappedList


class ChatMembersList(WrappedList):
    """List of chat members with search and filtering capabilities."""

    def GetByUserId(self,
                    user_id: int) -> Optional[pyrogram.types.ChatMember]:
        """
        Get a chat member by user ID.

        Args:
            user_id: The user ID to search for

        Returns:
            The chat member if found, None otherwise
        """
        res = list(filter(lambda member: user_id == member.user.id, self.list_elements))
        return None if len(res) == 0 else res[0]

    def GetByUsername(self,
                      username: str) -> Optional[pyrogram.types.ChatMember]:
        """
        Get a chat member by username.

        Args:
            username: The username to search for

        Returns:
            The chat member if found, None otherwise
        """
        res = list(filter(lambda member: username == member.user.username, self.list_elements))
        return None if len(res) == 0 else res[0]

    def IsUserIdPresent(self,
                        user_id: int) -> bool:
        """
        Check if a user ID is present in the list.

        Args:
            user_id: The user ID to check

        Returns:
            True if the user ID is present, False otherwise
        """
        return self.GetByUserId(user_id) is not None

    def IsUsernamePresent(self,
                          username: str) -> bool:
        """
        Check if a username is present in the list.

        Args:
            username: The username to check

        Returns:
            True if the username is present, False otherwise
        """
        return self.GetByUsername(username) is not None

    def ToString(self) -> str:
        """
        Convert the chat members list to a formatted string.

        Returns:
            A formatted string with all members
        """
        return "\n".join([f"- {UserHelper.GetNameOrId(member.user)}" for member in self.list_elements])

    def __str__(self) -> str:
        """
        Convert the chat members list to a formatted string.

        Returns:
            A formatted string with all members
        """
        return self.ToString()


class ChatMembersGetter:
    """Class for retrieving and filtering chat members."""

    client: pyrogram.Client

    def __init__(self,
                 client: pyrogram.Client) -> None:
        """
        Initialize the chat members getter.

        Args:
            client: The Pyrogram client instance
        """
        self.client = client

    async def FilterMembers(self,
                            chat: pyrogram.types.Chat,
                            filter_fct: Optional[Callable[[pyrogram.types.ChatMember], bool]] = None,
                            filter_type: ChatMembersFilter = ChatMembersFilter.SEARCH) -> ChatMembersList:
        """
        Get the list of chat members by applying the specified filter.

        Args:
            chat: The chat to get members from
            filter_fct: Optional filter function to apply to members
            filter_type: Pyrogram filter

        Returns:
            A sorted and filtered list of chat members
        """
        filtered_members = [member async for member in self.client.get_chat_members(chat.id, filter=filter_type)]     # type: ignore
        if filter_fct is not None:
            filtered_members = list(filter(filter_fct, filtered_members))  # type: ignore
        filtered_members.sort(  # type: ignore
            key=lambda member: member.user.username.lower() if member.user.username is not None else str(member.user.id)
        )

        chat_members = ChatMembersList()
        chat_members.AddMultiple(filtered_members)  # type: ignore

        return chat_members

    async def GetAll(self,
                     chat: pyrogram.types.Chat) -> ChatMembersList:
        """
        Get all members from a chat.

        Args:
            chat: The chat to get members from

        Returns:
            A list of all chat members
        """
        return await self.FilterMembers(chat)

    async def GetSingle(self,
                        chat: pyrogram.types.Chat,
                        user: pyrogram.types.User) -> ChatMembersList:
        """
        Get a single member from a chat.

        Args:
            chat: The chat to get the member from
            user: The user to get

        Returns:
            A list containing the single chat member
        """
        return await self.FilterMembers(chat, lambda member: member.user is not None and user.id == member.user.id)

    async def GetAdmins(self,
                        chat: pyrogram.types.Chat) -> ChatMembersList:
        """
        Get all administrators from a chat.

        Args:
            chat: The chat to get administrators from

        Returns:
            A list of all chat administrators
        """
        return await self.FilterMembers(chat,
                                        lambda member: True,
                                        ChatMembersFilter.ADMINISTRATORS)
