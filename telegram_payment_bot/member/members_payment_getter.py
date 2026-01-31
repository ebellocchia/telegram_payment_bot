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

from typing import Any, Dict, Optional

import pyrogram

from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.chat_members import ChatMembersGetter, ChatMembersList
from telegram_payment_bot.misc.helpers import MemberHelper
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentsData, SinglePayment
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase
from telegram_payment_bot.payment.payments_loader_factory import PaymentsLoaderFactory


class MembersPaymentGetter:
    """Getter for chat members and emails based on payment status."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    payments_loader: PaymentsLoaderBase
    payments_cache: Optional[PaymentsData]
    single_payment_cache: Optional[Dict[str, Any]]

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """Initialize the members payment getter.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.payments_loader = PaymentsLoaderFactory(config, logger).CreateLoader()
        self.payments_cache = None
        self.single_payment_cache = None

    def ReloadPayment(self):
        """Reload payment data by clearing the cache."""
        self.payments_cache = None
        self.single_payment_cache = None

    async def GetAllMembersWithOkPayment(self,
                                         chat: pyrogram.types.Chat) -> ChatMembersList:
        """Get all members with valid (non-expired) payments.

        Args:
            chat: Chat to get members from

        Returns:
            List of chat members with valid payments
        """
        payments = await self.__GetAllPayments()

        return await ChatMembersGetter(self.client).FilterMembers(
            chat,
            lambda member: (
                MemberHelper.IsValidMember(member) and
                member.user is not None and
                member.user.username is not None and
                not payments.IsExpiredByUser(User.FromUserObject(self.config, member.user))
            )
        )

    async def GetAllMembersWithExpiredPayment(self,
                                              chat: pyrogram.types.Chat) -> ChatMembersList:
        """Get all members with expired payments or no username.

        Args:
            chat: Chat to get members from

        Returns:
            List of chat members with expired payments
        """
        payments = await self.__GetAllPayments()

        if payments.Empty():
            return ChatMembersList()

        return await ChatMembersGetter(self.client).FilterMembers(
            chat,
            lambda member: (
                MemberHelper.IsValidMember(member) and
                member.user is not None and
                (member.user.username is None or
                 payments.IsExpiredByUser(User.FromUserObject(self.config, member.user)))
            )
        )

    async def GetAllMembersWithExpiringPayment(self,
                                               chat: pyrogram.types.Chat,
                                               days: int) -> ChatMembersList:
        """Get all members with payments expiring within specified days.

        Args:
            chat: Chat to get members from
            days: Number of days to check for expiration

        Returns:
            List of chat members with expiring payments
        """
        payments = await self.__GetAllPayments()

        if payments.Empty():
            return ChatMembersList()

        return await ChatMembersGetter(self.client).FilterMembers(
            chat,
            lambda member: (
                MemberHelper.IsValidMember(member) and
                member.user is not None and
                (member.user.username is None or
                 payments.IsExpiringInDaysByUser(User.FromUserObject(self.config, member.user), days))
            )
        )

    async def GetAllEmailsWithExpiredPayment(self) -> PaymentsData:
        """Get all emails with expired payments.

        Returns:
            PaymentsData containing expired payments
        """
        return (await self.__GetAllPayments()).FilterExpired()

    async def GetAllEmailsWithExpiringPayment(self,
                                              days: int) -> PaymentsData:
        """Get all emails with payments expiring within specified days.

        Args:
            days: Number of days to check for expiration

        Returns:
            PaymentsData containing expiring payments
        """
        return (await self.__GetAllPayments()).FilterExpiringInDays(days)

    async def IsSingleMemberExpired(self,
                                    chat: pyrogram.types.Chat,
                                    user: pyrogram.types.User) -> bool:
        """Check if a single member's payment is expired.

        Args:
            chat: Chat to check membership in
            user: User to check

        Returns:
            True if the payment is expired, False otherwise
        """
        chat_members = await ChatMembersGetter(self.client).GetSingle(chat, user)
        if chat_members is None:
            return False

        single_payment = await self.__GetSinglePayment(user)
        return single_payment.IsExpired() if single_payment is not None else True

    async def __GetAllPayments(self) -> PaymentsData:
        """Get all payments, loading them if not cached.

        Returns:
            PaymentsData containing all payments
        """
        if self.payments_cache is None:
            self.payments_cache = await self.payments_loader.LoadAll()

        return self.payments_cache

    async def __GetSinglePayment(self,
                                 user: pyrogram.types.User) -> Optional[SinglePayment]:
        """Get a single user's payment, loading it if not cached.

        Args:
            user: User to get payment for

        Returns:
            SinglePayment for the user, or None if not found
        """
        if self.single_payment_cache is None or self.single_payment_cache["user_id"] != user.id:
            self.single_payment_cache = {
                "payment": await self.payments_loader.LoadSingleByUser(User.FromUserObject(self.config, user)),
                "user_id": user.id,
            }

        return self.single_payment_cache["payment"]
