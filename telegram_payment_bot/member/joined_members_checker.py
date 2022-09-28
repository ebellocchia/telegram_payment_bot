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
from typing import List

import pyrogram

from telegram_payment_bot.auth_user.authorized_users_message_sender import AuthorizedUsersMessageSender
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_kicker import MembersKicker
from telegram_payment_bot.misc.helpers import UserHelper
from telegram_payment_bot.translator.translation_loader import TranslationLoader


#
# Classes
#

#
# Joined members checker class
#
class JoinedMembersChecker:

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    auth_users_msg_sender: AuthorizedUsersMessageSender
    member_kicker: MembersKicker

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.auth_users_msg_sender = AuthorizedUsersMessageSender(client, config, logger)
        self.member_kicker = MembersKicker(client, config, logger)

    # Check new users
    def CheckNewUsers(self,
                      chat: pyrogram.types.Chat,
                      new_users: List[pyrogram.types.User]) -> None:
        # Check all the new users
        for user in new_users:
            # Skip bots
            if not user.is_self and not user.is_bot:
                self.__CheckSingleUser(chat, user)

    # Check single user
    def __CheckSingleUser(self,
                          chat: pyrogram.types.Chat,
                          user: pyrogram.types.User) -> None:
        # Kick if no username
        if self.member_kicker.KickSingleIfNoUsername(chat, user):
            self.logger.GetLogger().info(
                f"New user {UserHelper.GetNameOrId(user)} kicked (joined with no username)"
            )
            self.auth_users_msg_sender.SendMessage(
                chat,
                self.translator.GetSentence("JOINED_MEMBER_KICKED_FOR_USERNAME_MSG",
                                            name=UserHelper.GetNameOrId(user))
            )
        # Kick if no payment
        elif self.member_kicker.KickSingleIfExpiredPayment(chat, user):
            self.logger.GetLogger().info(
                f"New user {UserHelper.GetNameOrId(user)} kicked (joined with no payment)"
            )
            self.auth_users_msg_sender.SendMessage(
                chat,
                self.translator.GetSentence("JOINED_MEMBER_KICKED_FOR_PAYMENT_MSG",
                                            name=UserHelper.GetNameOrId(user))
            )
        # Everything ok
        else:
            self.logger.GetLogger().info(
                f"New user {UserHelper.GetNameOrId(user)} joined, username and payment ok"
            )
