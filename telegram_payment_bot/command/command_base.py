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

from abc import ABC, abstractmethod
from typing import Any

import pyrogram
from pyrogram.errors import RPCError

from telegram_payment_bot.auth_user.authorized_users_list import AuthorizedUsersList
from telegram_payment_bot.auth_user.authorized_users_message_sender import AuthorizedUsersMessageSender
from telegram_payment_bot.command.command_data import CommandData
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.message.message_sender import MessageSender
from telegram_payment_bot.misc.helpers import ChatHelper, UserHelper
from telegram_payment_bot.translator.translation_loader import TranslationLoader


class CommandBase(ABC):
    """Base class for bot commands."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    message: pyrogram.types.Message
    cmd_data: CommandData
    message_sender: MessageSender

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """
        Constructor.

        Args:
            client: Pyrogram client
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.message_sender = MessageSender(client, logger)

    async def Execute(self,
                      message: pyrogram.types.Message,
                      **kwargs: Any) -> None:
        """
        Execute the command.

        Args:
            message: Telegram message containing the command
            **kwargs: Additional keyword arguments
        """
        self.message = message
        self.cmd_data = CommandData(message)

        self.__LogCommand()

        if self._IsUserAnonymous() and not self._IsChannel():
            self.logger.GetLogger().warning("An anonymous user tried to execute the command, exiting")
            return

        if not self._IsUserAuthorized():
            if self._IsPrivateChat():
                await self._SendMessage(self.translator.GetSentence("AUTH_ONLY_ERR_MSG"))

            self.logger.GetLogger().warning(
                f"User {UserHelper.GetNameOrId(self.cmd_data.User())} tried to execute the command but it's not authorized"
            )
            return

        try:
            await self._ExecuteCommand(**kwargs)
        except RPCError:
            await self._SendMessage(self.translator.GetSentence("GENERIC_ERR_MSG"))
            self.logger.GetLogger().exception(f"An error occurred while executing command {self.cmd_data.Name()}")

    async def _SendMessage(self,
                           msg: str) -> None:
        """
        Send a message.

        Args:
            msg: Message to send
        """
        if self._IsQuietMode():
            cmd_user = self.cmd_data.User()
            if not self._IsChannel() and cmd_user is not None:
                await self.message_sender.SendMessage(cmd_user, self.message.message_thread_id, msg)
            else:
                await self._SendMessageToAuthUsers(msg)
        else:
            await self.message_sender.SendMessage(self.cmd_data.Chat(), self.message.message_thread_id, msg)

    async def _SendMessageToAuthUsers(self,
                                      msg: str) -> None:
        """
        Send a message to authorized users.

        Args:
            msg: Message to send
        """
        await AuthorizedUsersMessageSender(self.client, self.config, self.logger).SendMessage(self.cmd_data.Chat(), msg)

    def _IsChannel(self) -> bool:
        """
        Check if command was executed in a channel.

        Returns:
            True if channel, False otherwise
        """
        return ChatHelper.IsChannel(self.cmd_data.Chat())

    def _IsUserAnonymous(self) -> bool:
        """
        Check if user is anonymous.

        Returns:
            True if user is anonymous, False otherwise
        """
        return self.cmd_data.User() is None

    def _IsUserAuthorized(self) -> bool:
        """
        Check if user is authorized.

        Returns:
            True if user is authorized, False otherwise
        """
        if not self._IsChannel():
            user = self.cmd_data.User()
            return user is not None and AuthorizedUsersList(self.config).IsUserPresent(user)
        return True

    def _IsPrivateChat(self) -> bool:
        """
        Check if chat is private.

        Returns:
            True if private chat, False otherwise
        """
        cmd_user = self.cmd_data.User()
        if cmd_user is None:
            return False
        return ChatHelper.IsPrivateChat(self.cmd_data.Chat(), cmd_user)

    def _IsQuietMode(self) -> bool:
        """
        Check if quiet mode is enabled.

        Returns:
            True if quiet mode is enabled, False otherwise
        """
        return self.cmd_data.Params().IsLast("q") or self.cmd_data.Params().IsLast("quiet")

    async def _NewInviteLink(self) -> None:
        """Generate and send a new invite link."""
        invite_link = await self.client.export_chat_invite_link(self.cmd_data.Chat().id)
        await self._SendMessage(self.translator.GetSentence("INVITE_LINK_ALL_CMD"))
        await self._SendMessageToAuthUsers(
            self.translator.GetSentence(
                "INVITE_LINK_AUTH_CMD",
                chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()),
                invite_link=invite_link
            )
        )

    def __LogCommand(self) -> None:
        """Log command execution details."""
        self.logger.GetLogger().info(f"Command: {self.cmd_data.Name()}")
        self.logger.GetLogger().info(f"Executed by user: {UserHelper.GetNameOrId(self.cmd_data.User())}")
        self.logger.GetLogger().debug(f"Received message: {self.message}")

    @abstractmethod
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the command implementation.

        Args:
            **kwargs: Additional keyword arguments
        """
