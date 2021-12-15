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
from abc import ABC, abstractmethod
from typing import Any
import pyrogram
from pyrogram.errors import RPCError
from telegram_payment_bot.auth_user.authorized_users_list import AuthorizedUsersList
from telegram_payment_bot.auth_user.authorized_users_message_sender import AuthorizedUsersMessageSender
from telegram_payment_bot.command.command_data import CommandData
from telegram_payment_bot.config.configurable_object import ConfigurableObject
from telegram_payment_bot.misc.helpers import ChatHelper, UserHelper
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.message.message_sender import MessageSender
from telegram_payment_bot.translator.translation_loader import TranslationLoader


#
# Classes
#

#
# Generic command base class
#
class CommandBase(ABC):

    client: pyrogram.Client
    config: ConfigurableObject
    logger: Logger
    translator: TranslationLoader
    message: pyrogram.types.Message
    cmd_data: CommandData
    message_sender: MessageSender

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
        self.message_sender = MessageSender(client, logger)

    # Execute command
    def Execute(self,
                message: pyrogram.types.Message,
                **kwargs: Any) -> None:
        # Set members
        self.message = message
        self.cmd_data = CommandData(message)

        # Log command
        self.__LogCommand()

        # Check if user is anonymous
        if self._IsUserAnonymous():
            self.logger.GetLogger().warning("An anonymous user tried to execute the command, exiting")
            return

        # Check if user is authorized
        if not self._IsUserAuthorized():
            if self._IsPrivateChat():
                self._SendMessage(self.translator.GetSentence("AUTH_ONLY_ERR_MSG"))

            self.logger.GetLogger().warning(
                f"User {UserHelper.GetNameOrId(self.cmd_data.User())} tried to execute the command but it's not authorized"
            )
            return

        # Try to execute command
        try:
            self._ExecuteCommand(**kwargs)
        except RPCError:
            self._SendMessage(self.translator.GetSentence("GENERIC_ERR_MSG"))
            self.logger.GetLogger().exception(
                f"An error occurred while executing command {self.cmd_data.Name()}"
            )

    # Send message
    def _SendMessage(self,
                     msg: str) -> None:
        if self._IsQuietMode():
            if not ChatHelper.IsChannel(self.cmd_data.Chat()):
                self.message_sender.SendMessage(self.cmd_data.User(), msg)
            else:
                self._SendMessageToAuthUsers(msg)
        else:
            self.message_sender.SendMessage(self.cmd_data.Chat(), msg)

    # Send message to authorized users
    def _SendMessageToAuthUsers(self,
                                msg: str) -> None:
        AuthorizedUsersMessageSender(self.client,
                                     self.config,
                                     self.logger).SendMessage(self.cmd_data.Chat(), msg)

    # Get if user is anonymous
    def _IsUserAnonymous(self) -> bool:
        return self.cmd_data.User() is None

    # Get if user is authorized
    def _IsUserAuthorized(self) -> bool:
        if self.cmd_data.User() is None:
            return False

        if not ChatHelper.IsChannel(self.cmd_data.Chat()):
            return AuthorizedUsersList(self.config).IsUserPresent(self.cmd_data.User())
        # In channels only admins can write, so we consider the user authorized since there is no way to know the specific user
        # This is a limitation for channels only
        return True

    # Get if chat is private
    def _IsPrivateChat(self) -> bool:
        return ChatHelper.IsPrivateChat(self.cmd_data.Chat(), self.cmd_data.User())

    # Get if quiet mode
    def _IsQuietMode(self) -> bool:
        return self.cmd_data.Params().IsLast("q") or self.cmd_data.Params().IsLast("quiet")

    # Generate new invite link
    def _NewInviteLink(self) -> None:
        # Generate new invite link
        invite_link = self.client.export_chat_invite_link(self.cmd_data.Chat().id)
        # Send messages
        self._SendMessage(self.translator.GetSentence("INVITE_LINK_ALL_CMD"))
        self._SendMessageToAuthUsers(
            self.translator.GetSentence("INVITE_LINK_AUTH_CMD",
                                        chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()),
                                        invite_link=invite_link)
        )

    # Log command
    def __LogCommand(self) -> None:
        self.logger.GetLogger().info(f"Command: {self.cmd_data.Name()}")
        self.logger.GetLogger().info(f"Executed by user: {UserHelper.GetNameOrId(self.cmd_data.User())}")
        self.logger.GetLogger().debug(f"Received message: {self.message}")

    # Execute command - Abstract method
    @abstractmethod
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        pass
