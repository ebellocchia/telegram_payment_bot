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

import pyrogram

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_payment_getter import MembersPaymentGetter
from telegram_payment_bot.member.members_username_getter import MembersUsernameGetter
from telegram_payment_bot.misc.ban_helper import BanHelper
from telegram_payment_bot.misc.chat_members import ChatMembersList


class MembersKickerConst:
    """Constants for members kicker class."""

    SLEEP_TIME_SEC: float = 0.01


class MembersKicker:
    """Kicker for chat members based on payment and username criteria."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    ban_helper: BanHelper
    members_payment_getter: MembersPaymentGetter
    members_username_getter: MembersUsernameGetter

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """Initialize the members kicker.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.ban_helper = BanHelper(client)
        self.members_payment_getter = MembersPaymentGetter(client, config, logger)
        self.members_username_getter = MembersUsernameGetter(client, config)

    async def KickAllWithExpiredPayment(self,
                                        chat: pyrogram.types.Chat) -> ChatMembersList:
        """Kick all members with expired payments from the chat.

        Args:
            chat: Chat to kick members from

        Returns:
            List of kicked members
        """
        no_payment_members = await self.members_payment_getter.GetAllMembersWithExpiredPayment(chat)
        if no_payment_members.Any():
            await self.__KickMultiple(chat, no_payment_members)
        return no_payment_members

    async def KickSingleIfExpiredPayment(self,
                                         chat: pyrogram.types.Chat,
                                         user: pyrogram.types.User) -> bool:
        """Kick a single member if their payment is expired.

        Args:
            chat: Chat to kick member from
            user: User to check and kick if expired

        Returns:
            True if the user was kicked, False otherwise
        """
        payment_expired = await self.members_payment_getter.IsSingleMemberExpired(chat, user)
        if payment_expired:
            await self.__KickSingle(chat, user)
        return payment_expired

    async def KickAllWithNoUsername(self,
                                    chat: pyrogram.types.Chat) -> ChatMembersList:
        """Kick all members without usernames from the chat.

        Args:
            chat: Chat to kick members from

        Returns:
            List of kicked members
        """
        no_username_members = await self.members_username_getter.GetAllWithNoUsername(chat)
        if no_username_members.Any():
            await self.__KickMultiple(chat, no_username_members)
        return no_username_members

    async def KickSingleIfNoUsername(self,
                                     chat: pyrogram.types.Chat,
                                     user: pyrogram.types.User) -> bool:
        """Kick a single member if they have no username.

        Args:
            chat: Chat to kick member from
            user: User to check and kick if no username

        Returns:
            True if the user was kicked, False otherwise
        """
        no_username = user.username is None
        if no_username:
            await self.__KickSingle(chat, user)
        return no_username

    async def __KickSingle(self,
                           chat: pyrogram.types.Chat,
                           user: pyrogram.types.User) -> None:
        """Kick a single member from the chat.

        Args:
            chat: Chat to kick member from
            user: User to kick
        """
        if not self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            await self.ban_helper.KickUser(chat, user)
        else:
            self.logger.GetLogger().info("Test mode ON: no member was kicked")

    async def __KickMultiple(self,
                             chat: pyrogram.types.Chat,
                             members: ChatMembersList) -> None:
        """Kick multiple members from the chat.

        Args:
            chat: Chat to kick members from
            members: List of members to kick
        """
        if not self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            for member in members:
                await self.ban_helper.KickUser(chat, member.user)
                await asyncio.sleep(MembersKickerConst.SLEEP_TIME_SEC)
        else:
            self.logger.GetLogger().info("Test mode ON: no member was kicked")
