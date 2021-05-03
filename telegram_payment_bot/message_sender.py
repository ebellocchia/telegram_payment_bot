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
import time
from typing import List, Union
from telegram_payment_bot.chat_members import ChatMembersGetter
from telegram_payment_bot.config import Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.helpers import UserHelper


#
# Classes
#

# Constant for message sender class
class MessageSenderConst:
    # Maximum message length
    MSG_MAX_LEN: int = 4096
    # Sleep time for sending messages
    SEND_MSG_SLEEP_TIME_SEC: float = 0.1


# Message sender class
class MessageSender:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger) -> None:
        self.client = client
        self.config = config
        self.logger = logger

    # Send message
    def SendMessage(self,
                    receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                    msg: str,
                    **kwargs) -> None:
        # Log
        self.logger.GetLogger().info("Sending message (length: %d):\n%s" % (len(msg), msg))
        # Split and send message
        self.__SendSplitMessage(receiver, self.__SplitMessage(msg), **kwargs)

    # Send message to authorized users
    def SendMessageToAuthUsers(self,
                               chat: pyrogram.types.Chat,
                               msg: str) -> None:
        # Log
        self.logger.GetLogger().info("Sending message to authorized users:\n%s" % msg)
        # Split message
        split_msg = self.__SplitMessage(msg)

        # Send to authorized users
        auth_members = ChatMembersGetter(self.client, self.config).GetAuthorizedUsers(chat)
        for auth_member in auth_members:
            self.__SendSplitMessage(auth_member.user, split_msg)
            self.logger.GetLogger().info(
                "Message sent to authorized user: %s" % UserHelper.GetNameOrId(auth_member.user))

    # Send split message
    def __SendSplitMessage(self,
                           receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                           split_msg: List[str],
                           **kwargs) -> None:
        # Send message
        for msg_part in split_msg:
            self.client.send_message(receiver.id, msg_part, **kwargs)
            time.sleep(MessageSenderConst.SEND_MSG_SLEEP_TIME_SEC)

    # Split message
    def __SplitMessage(self, msg: str) -> List[str]:
        msg_parts = []

        while len(msg) > 0:
            # If length is less than maximum, the operation is completed
            if len(msg) <= MessageSenderConst.MSG_MAX_LEN:
                msg_parts.append(msg)
                break
            else:
                # Take the current part
                curr_part = msg[:MessageSenderConst.MSG_MAX_LEN]
                # Get the last occurrence of a new line
                idx = curr_part.rfind("\n")

                # Split with respect to the found occurrence
                if idx != -1:
                    msg_parts.append(curr_part[:idx])
                    msg = msg[idx + 1:]
                else:
                    msg_parts.append(curr_part)
                    msg = msg[MessageSenderConst.MSG_MAX_LEN + 1:]

        # Log
        self.logger.GetLogger().info("Message split into %d part(s)" % len(msg_parts))

        return msg_parts
