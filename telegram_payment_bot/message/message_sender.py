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
import time
from typing import Any, List, Union
import pyrogram
from telegram_payment_bot.logger.logger import Logger


#
# Classes
#

# Constants for message sender class
class MessageSenderConst:
    # Maximum message length
    MSG_MAX_LEN: int = 4096
    # Sleep time for sending messages
    SEND_MSG_SLEEP_TIME_SEC: float = 0.1


# Message sender class
class MessageSender:

    client: pyrogram.Client
    logger: Logger

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        self.client = client
        self.logger = logger

    # Send message
    def SendMessage(self,
                    receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                    msg: str,
                    **kwargs: Any) -> List[pyrogram.types.Message]:
        # Log
        self.logger.GetLogger().debug(f"Sending message (length: {len(msg)}):\n{msg}")
        # Split and send message
        return self.__SendSplitMessage(receiver, self.__SplitMessage(msg), **kwargs)

    # Send split message
    def __SendSplitMessage(self,
                           receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                           split_msg: List[str],
                           **kwargs: Any) -> List[pyrogram.types.Message]:
        sent_msgs = []

        # Send message
        for msg_part in split_msg:
            sent_msgs.append(self.client.send_message(receiver.id, msg_part, **kwargs))
            time.sleep(MessageSenderConst.SEND_MSG_SLEEP_TIME_SEC)

        return sent_msgs

    # Split message
    def __SplitMessage(self,
                       msg: str) -> List[str]:
        msg_parts = []

        while len(msg) > 0:
            # If length is less than maximum, the operation is completed
            if len(msg) <= MessageSenderConst.MSG_MAX_LEN:
                msg_parts.append(msg)
                break

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
        self.logger.GetLogger().info(f"Message split into {len(msg_parts)} part(s)")

        return msg_parts
