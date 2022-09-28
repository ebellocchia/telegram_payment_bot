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
from threading import Lock

import pyrogram

from telegram_payment_bot.auth_user.authorized_users_message_sender import AuthorizedUsersMessageSender
from telegram_payment_bot.config.configurable_object import ConfigurableObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_kicker import MembersKicker
from telegram_payment_bot.misc.helpers import ChatHelper
from telegram_payment_bot.translator.translation_loader import TranslationLoader
from telegram_payment_bot.utils.wrapped_dict import WrappedDict


#
# Classes
#

# Payments check job chats class
class PaymentsCheckJobChats(WrappedDict):
    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [f"- {ChatHelper.GetTitle(chat)}" for _, chat in self.dict_elements.items()]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Payments check job class
class PaymentsCheckJob:

    client: pyrogram.Client
    config: ConfigurableObject
    logger: Logger
    translator: TranslationLoader
    job_chats_lock: Lock
    period: int
    auth_users_msg_sender: AuthorizedUsersMessageSender
    job_chats: PaymentsCheckJobChats

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigurableObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.job_chats_lock = Lock()
        self.period = 0
        self.auth_users_msg_sender = AuthorizedUsersMessageSender(client, config, logger)
        self.job_chats = PaymentsCheckJobChats()

    # Get period
    def GetPeriod(self) -> int:
        return self.period

    # Set period
    def SetPeriod(self,
                  period: int) -> None:
        self.period = period

    # Add chat
    def AddChat(self,
                chat: pyrogram.types.Chat) -> bool:
        # Prevent accidental modifications while job is executing
        with self.job_chats_lock:
            if self.job_chats.IsKey(chat.id):
                return False

            self.job_chats.AddSingle(chat.id, chat)
            return True

    # Remove chat
    def RemoveChat(self,
                   chat: pyrogram.types.Chat) -> bool:
        # Prevent accidental modifications while job is executing
        with self.job_chats_lock:
            if not self.job_chats.IsKey(chat.id):
                return False

            self.job_chats.RemoveSingle(chat.id)
            return True

    # Remove all chats
    def RemoveAllChats(self) -> None:
        # Prevent accidental modifications while job is executing
        with self.job_chats_lock:
            self.job_chats.Clear()

    # Get chat list
    def GetChats(self) -> PaymentsCheckJobChats:
        return self.job_chats

    # Do job
    def DoJob(self) -> None:
        # Log
        self.logger.GetLogger().info("Payments check job started")

        # Lock
        with self.job_chats_lock:
            # Exit if no chats
            if self.job_chats.Empty():
                self.logger.GetLogger().info("No chat to check, exiting...")
                return

            # Kick members for each chat
            members_kicker = MembersKicker(self.client, self.config, self.logger)
            for _, chat in self.job_chats.Items():
                self.__KickMembersInChat(chat, members_kicker)

    # Kick members in chat
    def __KickMembersInChat(self,
                            chat: pyrogram.types.Chat,
                            members_kicker: MembersKicker) -> None:
        # Kick all members
        self.logger.GetLogger().info(f"Checking payments for chat {ChatHelper.GetTitleOrId(chat)}...")
        kicked_members = members_kicker.KickAllWithExpiredPayment(chat)

        # Log kicked members
        self.logger.GetLogger().info(
            f"Kicked members for chat {ChatHelper.GetTitleOrId(chat)}: {kicked_members.Count()}"
        )
        if kicked_members.Any():
            self.logger.GetLogger().info(str(kicked_members))

            # Inform authorized users
            msg = self.translator.GetSentence("REMOVE_NO_PAYMENT_NOTICE_CMD",
                                              chat_title=ChatHelper.GetTitle(chat))
            msg += "\n\n"
            msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_COMPLETED_CMD",
                                               members_count=kicked_members.Count())
            msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_LIST_CMD",
                                               members_list=str(kicked_members))

            self.auth_users_msg_sender.SendMessage(chat, msg)
