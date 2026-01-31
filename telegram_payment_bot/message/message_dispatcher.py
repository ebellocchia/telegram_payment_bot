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

from enum import Enum, auto, unique
from typing import Any

import pyrogram

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.joined_members_checker import JoinedMembersChecker
from telegram_payment_bot.message.message_sender import MessageSender
from telegram_payment_bot.translator.translation_loader import TranslationLoader


@unique
class MessageTypes(Enum):
    """Message types enumeration."""
    GROUP_CHAT_CREATED = auto()
    LEFT_CHAT_MEMBER = auto()
    NEW_CHAT_MEMBERS = auto()


class MessageDispatcher:
    """Message dispatcher for handling different message types."""

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """
        Constructor.

        Args:
            config: Configuration object
            logger: Logger object
            translator: Translation loader object
        """
        self.config = config
        self.logger = logger
        self.translator = translator

    async def Dispatch(self,
                       client: pyrogram.Client,
                       message: pyrogram.types.Message,
                       msg_type: MessageTypes,
                       **kwargs: Any) -> None:
        """
        Dispatch a message based on its type.

        Args:
            client: Pyrogram client
            message: Message object
            msg_type: Type of message to dispatch
            **kwargs: Additional arguments

        Raises:
            TypeError: If msg_type is not a MessageTypes enum
        """
        if not isinstance(msg_type, MessageTypes):
            raise TypeError("Message type is not an enumerative of MessageTypes")

        # Log
        self.logger.GetLogger().info(f"Dispatching message type: {msg_type}")

        # New chat created
        if msg_type == MessageTypes.GROUP_CHAT_CREATED:
            await self.__OnCreatedChat(client, message, **kwargs)
        # A member left the chat
        elif msg_type == MessageTypes.LEFT_CHAT_MEMBER:
            await self.__OnLeftMember(client, message, **kwargs)
        # A member joined the chat
        elif msg_type == MessageTypes.NEW_CHAT_MEMBERS:
            await self.__OnJoinedMember(client, message, **kwargs)

    async def __OnCreatedChat(self,
                              client,
                              message: pyrogram.types.Message,
                              **kwargs: Any) -> None:
        """
        Handle when a new chat is created.

        Args:
            client: Pyrogram client
            message: Message object
            **kwargs: Additional arguments
        """
        if message.chat is None:
            return

        # Send the welcome message
        await MessageSender(client, self.logger).SendMessage(
            message.chat,
            message.message_thread_id,
            self.translator.GetSentence("BOT_WELCOME_MSG")
        )

    async def __OnLeftMember(self,
                             client,
                             message: pyrogram.types.Message,
                             **kwargs: Any) -> None:
        """
        Handle when a member left the chat.

        Args:
            client: Pyrogram client
            message: Message object
            **kwargs: Additional arguments
        """
        # If the member is the bot itself, remove the chat from the scheduler
        if message.left_chat_member is not None and message.left_chat_member.is_self:
            kwargs["payments_check_scheduler"].ChatLeft(message.chat)

    async def __OnJoinedMember(self,
                               client,
                               message: pyrogram.types.Message,
                               **kwargs: Any) -> None:
        """
        Handle when a member joined the chat.

        Args:
            client: Pyrogram client
            message: Message object
            **kwargs: Additional arguments
        """
        if message.new_chat_members is None or message.chat is None:
            return

        # If one of the members is the bot itself, send the welcome message
        for member in message.new_chat_members:
            if member.is_self:
                await MessageSender(client, self.logger).SendMessage(
                    message.chat,
                    message.message_thread_id,
                    self.translator.GetSentence("BOT_WELCOME_MSG")
                )
                break

        # Check joined members for payment in any case
        if self.config.GetValue(BotConfigTypes.PAYMENT_CHECK_ON_JOIN):
            await JoinedMembersChecker(client,
                                       self.config,
                                       self.logger,
                                       self.translator).CheckNewUsers(message.chat, message.new_chat_members)
