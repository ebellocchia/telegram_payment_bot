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
import pyrogram.errors.exceptions as pyrogram_ex
from telegram_payment_bot.authorized_users_getter import AuthorizedUsersGetter
from telegram_payment_bot.config import Config
from telegram_payment_bot.helpers import UserHelper
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.message_sender import MessageSender


#
# Classes
#

# Authorized users message sender class
class AuthorizedUsersMessageSender:

    logger: Logger
    auth_users_getter: AuthorizedUsersGetter
    message_sender: MessageSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger) -> None:
        self.logger = logger
        self.auth_users_getter = AuthorizedUsersGetter(client, config)
        self.message_sender = MessageSender(client, logger)

    # Send message
    def SendMessage(self,
                    chat: pyrogram.types.Chat,
                    msg: str,
                    **kwargs) -> None:
        # Send to authorized users
        for auth_member in self.auth_users_getter.GetUsers(chat):
            try:
                self.message_sender.SendMessage(auth_member.user, msg, **kwargs)
                self.logger.GetLogger().info(
                    f"Message sent to authorized user: {UserHelper.GetNameOrId(auth_member.user)}"
                )
            # It may happen if the user has never talked to the bot or blocked it
            except (pyrogram_ex.bad_request_400.PeerIdInvalid,
                    pyrogram_ex.bad_request_400.UserIsBlocked):
                self.logger.GetLogger().error(
                    f"Unable to send message to authorized user: {UserHelper.GetNameOrId(auth_member.user)}"
                )
