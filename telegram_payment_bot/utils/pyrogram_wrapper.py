# Copyright (c) 2021-2026 Emanuele Bellocchia
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

# Old wrapper, not needed anymore with pyrotgfork

import time
from datetime import datetime, timedelta
from typing import Iterator

import pyrogram

from telegram_payment_bot.utils.utils import Utils


if int(pyrogram.__version__[0]) == 2:
    from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
else:
    from enum import Enum

    class ChatMembersFilter(Enum):      # type: ignore
        """Fake enum for Pyrogram v1 compatibility."""

    class ChatMemberStatus(Enum):       # type: ignore
        """Fake enum for Pyrogram v1 compatibility."""


class PyrogramWrapper:
    """Wrapper for pyrogram for handling different versions."""

    @staticmethod
    def BanChatMember(client: pyrogram.Client,
                      chat: pyrogram.types.Chat,
                      user: pyrogram.types.User,
                      time_sec: int = 0) -> None:
        """
        Ban chat member.

        Args:
            client: Pyrogram client
            chat: Chat object
            user: User to ban
            time_sec: Ban duration in seconds (0 for permanent)
        """
        if PyrogramWrapper.__MajorVersion() == 2:
            client.ban_chat_member(chat.id,
                                   user.id,
                                   until_date=datetime.now() + timedelta(seconds=time_sec))
        elif PyrogramWrapper.__MajorVersion() == 1:
            if PyrogramWrapper.__MinorVersion() >= 3:
                client.ban_chat_member(chat.id,
                                       user.id,
                                       until_date=int(time.time() + time_sec))
            else:
                client.kick_chat_member(chat.id,
                                        user.id,
                                        until_date=int(time.time() + time_sec))

    @staticmethod
    def MemberIsStatus(member: pyrogram.types.ChatMember,
                       status_str: str) -> bool:
        """
        Check if member has a specific status.

        Args:
            member: Chat member object
            status_str: Status string to check

        Returns:
            True if member has the status, False otherwise

        Raises:
            RuntimeError: If pyrogram version is unsupported
        """
        if PyrogramWrapper.__MajorVersion() == 2:
            return member.status == PyrogramWrapper.__StrToChatMemberStatus(status_str)
        if PyrogramWrapper.__MajorVersion() == 1:
            return member.status == status_str
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def MessageId(message: pyrogram.types.Message) -> int:
        """
        Get message ID.

        Args:
            message: Message object

        Returns:
            Message ID

        Raises:
            RuntimeError: If pyrogram version is unsupported
        """
        if PyrogramWrapper.__MajorVersion() == 2:
            return message.id
        if PyrogramWrapper.__MajorVersion() == 1:
            return message.message_id
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def IsChannel(chat: pyrogram.types.Chat) -> bool:
        """
        Check if chat is a channel.

        Args:
            chat: Chat object

        Returns:
            True if chat is a channel, False otherwise

        Raises:
            RuntimeError: If pyrogram version is unsupported
        """
        if PyrogramWrapper.__MajorVersion() == 2:
            return chat.type == ChatType.CHANNEL
        if PyrogramWrapper.__MajorVersion() == 1:
            return chat["type"] == "channel"
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def GetChatMembers(client: pyrogram.Client,
                       chat: pyrogram.types.Chat,
                       filter_str: str) -> Iterator[pyrogram.types.ChatMember]:
        """
        Get chat members.

        Args:
            client: Pyrogram client
            chat: Chat object
            filter_str: Filter string for member types

        Returns:
            Iterator of chat members

        Raises:
            RuntimeError: If pyrogram version is unsupported
        """
        if PyrogramWrapper.__MajorVersion() == 2:
            return client.get_chat_members(chat.id, filter=PyrogramWrapper.__StrToChatMembersFilter(filter_str))
        if PyrogramWrapper.__MajorVersion() == 1:
            return client.iter_chat_members(chat.id, filter=filter_str)
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def __StrToChatMembersFilter(filter_str: str) -> ChatMembersFilter:
        """
        Convert string to ChatMembersFilter enum.

        Args:
            filter_str: Filter string

        Returns:
            ChatMembersFilter enum value
        """
        str_to_enum = {
            "all": ChatMembersFilter.SEARCH,
            "banned": ChatMembersFilter.BANNED,
            "bots": ChatMembersFilter.BOTS,
            "restricted": ChatMembersFilter.RESTRICTED,
            "administrators": ChatMembersFilter.ADMINISTRATORS,
        }

        return str_to_enum[filter_str]

    @staticmethod
    def __StrToChatMemberStatus(status_str: str) -> ChatMemberStatus:
        """
        Convert string to ChatMemberStatus enum.

        Args:
            status_str: Status string

        Returns:
            ChatMemberStatus enum value
        """
        str_to_enum = {
            "owner": ChatMemberStatus.OWNER,
            "administrator": ChatMemberStatus.ADMINISTRATOR,
            "member": ChatMemberStatus.MEMBER,
            "restricted": ChatMemberStatus.RESTRICTED,
            "left": ChatMemberStatus.LEFT,
            "banned": ChatMemberStatus.BANNED,
        }

        return str_to_enum[status_str]

    @staticmethod
    def __MajorVersion() -> int:
        """
        Get major version of pyrogram.

        Returns:
            Major version number
        """
        return Utils.StrToInt(pyrogram.__version__[0])

    @staticmethod
    def __MinorVersion() -> int:
        """
        Get minor version of pyrogram.

        Returns:
            Minor version number
        """
        return Utils.StrToInt(pyrogram.__version__[2])
