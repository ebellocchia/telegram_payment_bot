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

from typing import Optional

import pyrogram
from pyrogram.enums import ChatMemberStatus, ChatType


class ChatHelper:
    """Helper class for chat-related operations."""

    @staticmethod
    def IsChannel(chat: pyrogram.types.Chat) -> bool:
        """
        Check if the chat is a channel.

        Args:
            chat: The chat to check

        Returns:
            True if the chat is a channel, False otherwise
        """
        return chat.type == ChatType.CHANNEL

    @staticmethod
    def GetTitle(chat: pyrogram.types.Chat) -> str:
        """
        Get the title of the chat.

        Args:
            chat: The chat to get the title from

        Returns:
            The chat title or an empty string if not available
        """
        return chat.title if chat.title is not None else ""

    @staticmethod
    def GetTitleOrId(chat: pyrogram.types.Chat) -> str:
        """
        Get the title and ID of the chat, or just the ID if title is not available.

        Args:
            chat: The chat to get the title or ID from

        Returns:
            A formatted string with the title and ID, or just the ID
        """
        return f"'{chat.title}' (ID: {chat.id})" if chat.title is not None else f"{chat.id}"

    @staticmethod
    def IsPrivateChat(chat: pyrogram.types.Chat,
                      user: pyrogram.types.User):
        """
        Check if the chat is a private chat between the bot and the user.

        Args:
            chat: The chat to check
            user: The user to check against

        Returns:
            True if the chat is a private chat, False otherwise
        """
        if ChatHelper.IsChannel(chat):
            return False
        return chat.id == user.id


class MemberHelper:
    """Helper class for chat member-related operations."""

    @staticmethod
    def IsValidMember(member: pyrogram.types.ChatMember) -> bool:
        """
        Check if a chat member is valid (not self, not bot, regular member status).

        Args:
            member: The chat member to check

        Returns:
            True if the member is valid, False otherwise
        """
        return (
            member.status == ChatMemberStatus.MEMBER
            and member.user is not None
            and (member.user.is_self is None or not member.user.is_self)
            and (member.user.is_bot is None or not member.user.is_bot)
        )


class UserHelper:
    """Helper class for user-related operations."""

    @staticmethod
    def GetNameOrId(user: Optional[pyrogram.types.User]) -> str:
        """
        Get the username, name, and ID of the user, or just the ID if name is not available.

        Args:
            user: The user to get information from

        Returns:
            A formatted string with the user information
        """
        if user is None:
            return "Anonymous user"

        if user.username is not None:
            return f"@{user.username} ({UserHelper.GetName(user)} - ID: {user.id})"

        name = UserHelper.GetName(user)
        return f"{name} (ID: {user.id})" if name is not None else f"ID: {user.id}"

    @staticmethod
    def GetName(user: Optional[pyrogram.types.User]) -> str:
        """
        Get the full name of the user (first name and last name).

        Args:
            user: The user to get the name from

        Returns:
            The user's full name or an empty string if not available
        """
        if user is None:
            return "Anonymous user"

        if user.first_name is not None:
            return f"{user.first_name} {user.last_name}" if user.last_name is not None else f"{user.first_name}"
        return user.last_name if user.last_name is not None else ""
