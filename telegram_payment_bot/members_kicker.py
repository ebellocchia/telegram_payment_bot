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
from telegram_payment_bot.ban_helper import BanHelper
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.chat_members import ChatMembersList
from telegram_payment_bot.payments_checker import PaymentsChecker
from telegram_payment_bot.username_checker import UsernameChecker


#
# Classes
#

# Members kicker class
class MembersKicker:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.ban_helper = BanHelper(self.client)
        self.payment_checker = PaymentsChecker(self.client, self.config, self.logger)
        self.username_checker = UsernameChecker(self.client, self.config)

    # Kick all members with expired payment
    def KickAllWithExpiredPayment(self,
                                  chat: pyrogram.types.Chat) -> ChatMembersList:
        # Get expired members
        no_payment_members = self.payment_checker.GetAllMembersWithExpiredPayment(chat)

        # Kick members if any (only if not test mode)
        if not self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            for member in no_payment_members:
                self.ban_helper.KickUser(chat, member.user)
        else:
            self.logger.GetLogger().info("Test mode ON: no member will be kicked")

        return no_payment_members

    # Kick single member if expired payment
    def KickSingleIfExpiredPayment(self,
                                   chat: pyrogram.types.Chat,
                                   user: pyrogram.types.User) -> bool:
        # Get expired members
        payment_expired = self.payment_checker.IsSingleMemberExpired(chat, user)

        if not self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            if payment_expired:
                self.ban_helper.KickUser(chat, user)
        else:
            self.logger.GetLogger().info("Test mode ON: no member will be kicked")

        return payment_expired

    # Kick all members with no username
    def KickAllWithNoUsername(self,
                              chat: pyrogram.types.Chat) -> ChatMembersList:
        # Get expired members
        no_username_members = self.username_checker.GetAllWithNoUsername(chat)

        # Kick members if any (only if not test mode)
        if not self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            for member in no_username_members:
                self.ban_helper.KickUser(chat, member.user)
        else:
            self.logger.GetLogger().info("Test mode ON: no member will be kicked")

        return no_username_members

    # Kick single member if no username
    def KickSingleIfNoUsername(self,
                               chat: pyrogram.types.Chat,
                               user: pyrogram.types.User) -> bool:
        no_username = user.username is None

        if not self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            if no_username:
                self.ban_helper.KickUser(chat, user)
        else:
            self.logger.GetLogger().info("Test mode ON: no member will be kicked")

        return no_username
