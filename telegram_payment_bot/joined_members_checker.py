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
from typing import List
from telegram_payment_bot.config import Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.members_kicker import MembersKicker
from telegram_payment_bot.user_helper import UserHelper


#
# Classes
#

#
# Joined members checker class
#
class JoinedMembersChecker:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.client = client
        self.member_kicker = MembersKicker(client, config, logger)

    # Check users
    def CheckUsers(self,
                   chat: pyrogram.types.Chat,
                   new_users: List[pyrogram.types.User]) -> None:
        # Check all the new users
        for user in new_users:
            self.__CheckSingleUser(chat, user)

    # Check single user
    def __CheckSingleUser(self,
                          chat: pyrogram.types.Chat,
                          user: pyrogram.types.User) -> None:
        # Kick if no username
        if self.member_kicker.KickSingleIfNoUsername(chat, user):
            self.logger.GetLogger().info("New user %s kicked (joined with no username)" % UserHelper.GetNameOrId(user))
        # Kick if no payment
        elif self.member_kicker.KickSingleIfExpiredPayment(chat, user):
            self.logger.GetLogger().info("New user %s kicked (joined with no payment)" % UserHelper.GetNameOrId(user))
        # Everything ok
        else:
            self.logger.GetLogger().info("New user %s joined, username and payment ok" % UserHelper.GetNameOrId(user))
