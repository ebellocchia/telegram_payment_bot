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

import asyncio

import pyrogram

from telegram_payment_bot.auth_user.authorized_users_message_sender import AuthorizedUsersMessageSender
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_kicker import MembersKicker
from telegram_payment_bot.misc.helpers import ChatHelper
from telegram_payment_bot.translator.translation_loader import TranslationLoader
from telegram_payment_bot.utils.wrapped_dict import WrappedDict


class PaymentsCheckJobChats(WrappedDict):
    """Collection of chats for the payments check job."""

    def ToString(self) -> str:
        """Convert to string representation.

        Returns:
            String representation with chat titles
        """
        return "\n".join(
            [f"- {ChatHelper.GetTitle(chat)}" for _, chat in self.dict_elements.items()]
        )

    def __str__(self) -> str:
        """Convert to string representation.

        Returns:
            String representation with chat titles
        """
        return self.ToString()


class PaymentsCheckJob:
    """Job for periodically checking and kicking members with expired payments."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    job_chats_lock: asyncio.Lock
    period: int
    auth_users_msg_sender: AuthorizedUsersMessageSender
    job_chats: PaymentsCheckJobChats

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the payments check job.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader instance
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.job_chats_lock = asyncio.Lock()
        self.period = 0
        self.auth_users_msg_sender = AuthorizedUsersMessageSender(client, config, logger)
        self.job_chats = PaymentsCheckJobChats()

    def GetPeriod(self) -> int:
        """Get the job period.

        Returns:
            Job period in hours
        """
        return self.period

    def SetPeriod(self,
                  period: int) -> None:
        """Set the job period.

        Args:
            period: Job period in hours
        """
        self.period = period

    async def AddChat(self,
                      chat: pyrogram.types.Chat) -> bool:
        """Add a chat to the job.

        Args:
            chat: Chat to add

        Returns:
            True if added successfully, False if chat already exists
        """
        async with self.job_chats_lock:
            if self.job_chats.IsKey(chat.id):
                return False

            self.job_chats.AddSingle(chat.id, chat)
            return True

    async def RemoveChat(self,
                         chat: pyrogram.types.Chat) -> bool:
        """Remove a chat from the job.

        Args:
            chat: Chat to remove

        Returns:
            True if removed successfully, False if chat not found
        """
        async with self.job_chats_lock:
            if not self.job_chats.IsKey(chat.id):
                return False

            self.job_chats.RemoveSingle(chat.id)
            return True

    async def RemoveAllChats(self) -> None:
        """Remove all chats from the job."""
        async with self.job_chats_lock:
            self.job_chats.Clear()

    def GetChats(self) -> PaymentsCheckJobChats:
        """Get the list of chats in the job.

        Returns:
            PaymentsCheckJobChats containing all chats
        """
        return self.job_chats

    async def DoJob(self) -> None:
        """Execute the payments check job."""
        self.logger.GetLogger().info("Payments check job started")

        async with self.job_chats_lock:
            if self.job_chats.Empty():
                self.logger.GetLogger().info("No chat to check, exiting...")
                return

            members_kicker = MembersKicker(self.client, self.config, self.logger)
            for chat in self.job_chats.Values():
                await self.__KickMembersInChat(chat, members_kicker)

    async def __KickMembersInChat(self,
                                  chat: pyrogram.types.Chat,
                                  members_kicker: MembersKicker) -> None:
        """Kick members with expired payments in a chat.

        Args:
            chat: Chat to check
            members_kicker: MembersKicker instance
        """
        self.logger.GetLogger().info(f"Checking payments for chat {ChatHelper.GetTitleOrId(chat)}...")
        kicked_members = await members_kicker.KickAllWithExpiredPayment(chat)

        self.logger.GetLogger().info(
            f"Kicked members for chat {ChatHelper.GetTitleOrId(chat)}: {kicked_members.Count()}"
        )
        if kicked_members.Any():
            self.logger.GetLogger().info(str(kicked_members))

            msg = self.translator.GetSentence("REMOVE_NO_PAYMENT_NOTICE_CMD",
                                              chat_title=ChatHelper.GetTitle(chat))
            msg += "\n\n"
            msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_COMPLETED_CMD",
                                               members_count=kicked_members.Count())
            msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_LIST_CMD",
                                               members_list=str(kicked_members))

            await self.auth_users_msg_sender.SendMessage(chat, msg)
