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
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.helpers import ChatHelper
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.members_kicker import MembersKicker
from telegram_payment_bot.message_sender import MessageSender
from telegram_payment_bot.translation_loader import TranslationLoader
from telegram_payment_bot.wrapped_dict import WrappedDict


#
# Classes
#

# Payment checker chats class
class PaymentCheckerChats(WrappedDict):
    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [f"- {ChatHelper.GetTitle(chat)}" for (_, chat) in self.dict_elements.items()]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Payments checker job class
class PaymentsCheckerJob:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.chats = PaymentCheckerChats()
        self.message_sender = MessageSender(client, config, logger)

    # Add chat
    def AddChat(self,
                chat: pyrogram.types.Chat) -> bool:
        if self.chats.IsKey(chat.id):
            return False

        self.chats.AddSingle(chat.id, chat)
        return True

    # Remove chat
    def RemoveChat(self,
                   chat: pyrogram.types.Chat) -> bool:
        if not self.chats.IsKey(chat.id):
            return False

        self.chats.RemoveSingle(chat.id)
        return True

    # Remove all chats
    def RemoveAllChats(self) -> None:
        self.chats.Clear()

    # Get chat list
    def GetChats(self) -> PaymentCheckerChats:
        return self.chats

    # Check payments
    def CheckPayments(self) -> None:
        # Log
        self.logger.GetLogger().info("Periodic payments check started")

        # Exit if no chats
        if self.chats.Empty():
            self.logger.GetLogger().info("No chat to check, exiting...")
            return

        # Kick members for each chat
        members_kicker = MembersKicker(self.client, self.config, self.logger)

        for chat in self.chats:
            chat_id = chat.id

            # Kick members
            self.logger.GetLogger().info(f"Checking payments for chat ID {chat_id}...")
            curr_chat = pyrogram.types.Chat(id=chat_id, type="supergroup")
            kicked_members = members_kicker.KickAllWithExpiredPayment(curr_chat)

            # Log kicked members
            self.logger.GetLogger().info(
                f"Kicked members for chat ID {chat_id}: {kicked_members.Count()}"
            )
            if kicked_members.Any():
                self.logger.GetLogger().info(str(kicked_members))

                # Inform authorized users
                msg = self.translator.GetSentence("REMOVE_NO_USERNAME_NOTICE_CMD",
                                                  chat_title=ChatHelper.GetTitle(chat))
                msg += "\n" + self.translator.GetSentence("REMOVE_NO_USERNAME_COMPLETED_CMD",
                                                          members_count=kicked_members.Count())
                msg += self.translator.GetSentence("REMOVE_NO_USERNAME_LIST_CMD",
                                                   members_list=str(kicked_members))

                self.message_sender.SendMessageToAuthUsers(curr_chat, msg)
