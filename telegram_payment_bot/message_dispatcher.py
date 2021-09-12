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
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.joined_members_checker import JoinedMembersChecker
from telegram_payment_bot.translation_loader import TranslationLoader


#
# Classes
#

#
# Message dispatcher class
#
class MessageDispatcher:
    # Constructor
    def __init__(self,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.translator = translator

    # Dispatch command
    def Dispatch(self,
                 client: pyrogram.Client,
                 message: pyrogram.types.Message) -> None:
        # New members joined
        if self.config.GetValue(ConfigTypes.PAYMENT_CHECK_ON_JOIN) and message.new_chat_members is not None:
            JoinedMembersChecker(client,
                                 self.config,
                                 self.logger,
                                 self.translator).CheckUsers(message.chat, message.new_chat_members)
