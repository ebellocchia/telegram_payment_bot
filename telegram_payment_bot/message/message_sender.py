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

import asyncio
from typing import Any, List, Union

import pyrogram

from telegram_payment_bot.logger.logger import Logger


class MessageSenderConst:
    """Constants for message sender."""

    MSG_MAX_LEN: int = 4096
    SEND_MSG_SLEEP_TIME_SEC: float = 0.1


class MessageSender:
    """Message sender for Telegram."""

    client: pyrogram.Client
    logger: Logger

    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        """
        Constructor.

        Args:
            client: Pyrogram client
            logger: Logger object
        """
        self.client = client
        self.logger = logger

    async def SendMessage(self,
                          receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                          topic_id: int,
                          msg: str,
                          **kwargs: Any) -> List[pyrogram.types.Message]:
        """
        Send a message to a receiver, splitting if necessary.

        Args:
            receiver: Chat or user to send the message to
            topic_id: Topic to send the message to
            msg: Message text to send
            **kwargs: Additional arguments to pass to send_message

        Returns:
            List of sent message objects
        """
        # Log
        self.logger.GetLogger().debug(f"Sending message (length: {len(msg)}):\n{msg}")
        # Split and send message
        return await self.__SendSplitMessage(receiver, topic_id, self.__SplitMessage(msg), **kwargs)

    async def __SendSplitMessage(self,
                                 receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                                 topic_id: int,
                                 split_msg: List[str],
                                 **kwargs: Any) -> List[pyrogram.types.Message]:
        """
        Send a message that has been split into multiple parts.

        Args:
            receiver: Chat or user to send the message to
            topic_id: Topic to send the message to
            split_msg: List of message parts
            **kwargs: Additional arguments to pass to send_message

        Returns:
            List of sent message objects
        """
        sent_msgs = []

        # Send message
        for msg_part in split_msg:
            sent_msg = await self.client.send_message(receiver.id, msg_part, message_thread_id=topic_id, **kwargs)
            sent_msgs.append(sent_msg)
            await asyncio.sleep(MessageSenderConst.SEND_MSG_SLEEP_TIME_SEC)

        return sent_msgs

    def __SplitMessage(self,
                       msg: str) -> List[str]:
        """
        Split a message into parts if it exceeds the maximum length.

        Args:
            msg: Message to split

        Returns:
            List of message parts
        """
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
