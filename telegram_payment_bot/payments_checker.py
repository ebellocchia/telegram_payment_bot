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
from typing import Optional
from telegram_payment_bot.config import Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.chat_members import ChatMembersList, ChatMembersGetter
from telegram_payment_bot.payments_loader_factory import PaymentsLoaderFactory
from telegram_payment_bot.payments_data import SinglePayment, PaymentsDict


#
# Classes
#

# Payments checker class
class PaymentsChecker:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.payments_loader = PaymentsLoaderFactory(self.config, self.logger).CreateLoader()
        self.payments_cache = None
        self.single_payment_cache = None

        self.ReloadPayment()

    # Reload payment
    def ReloadPayment(self):
        self.payments_cache = None
        self.single_payment_cache = None

    # Get all members with OK payment
    def GetAllMembersWithOkPayment(self,
                                   chat: pyrogram.types.Chat) -> ChatMembersList:
        # Get all payments
        payments = self.__GetAllPayments()

        # Filter chat members
        chat_members_getter = ChatMembersGetter(self.client, self.config)
        return chat_members_getter.FilterMembers(chat,
                                                 lambda member: member.status == "member" and
                                                                member.user.username is not None and
                                                                not payments.IsExpiredByUsername(member.user.username))

    # Get all members with expired payment
    def GetAllMembersWithExpiredPayment(self,
                                        chat: pyrogram.types.Chat) -> ChatMembersList:
        # Get all payments
        payments = self.__GetAllPayments()

        # For safety: if no data was loaded, no user is expired
        if payments.Empty():
            return ChatMembersList()

        # Filter chat members
        chat_members_getter = ChatMembersGetter(self.client, self.config)
        return chat_members_getter.FilterMembers(chat,
                                                 lambda member: member.status == "member" and
                                                                (member.user.username is None or
                                                                 payments.IsExpiredByUsername(member.user.username)))

    # Get all members with expiring payment
    def GetAllMembersWithExpiringPayment(self,
                                         chat: pyrogram.types.Chat,
                                         days: int) -> ChatMembersList:
        # Get all payments
        payments = self.__GetAllPayments()

        # For safety: if no data was loaded, no user is expired
        if payments.Empty():
            return ChatMembersList()

        # Filter chat members
        chat_members_getter = ChatMembersGetter(self.client, self.config)
        return chat_members_getter.FilterMembers(chat,
                                                 lambda member: member.status == "member" and
                                                                (member.user.username is None or
                                                                 payments.IsExpiringInDaysByUsername(member.user.username, days)))

    # Get all emails with expired payment
    def GetAllEmailsWithExpiredPayment(self) -> PaymentsDict:
        return self.__GetAllPayments().FilterExpired()

    # Get all emails with expiring payment in the specified number of days
    def GetAllEmailsWithExpiringPayment(self,
                                        days: int) -> PaymentsDict:
        return self.__GetAllPayments().FilterExpiringInDays(days)

    # Get if single member is expired
    def IsSingleMemberExpired(self,
                              chat: pyrogram.types.Chat,
                              user: pyrogram.types.User) -> bool:
        # If the user is not in the chat, consider payment as not expired
        chat_members = ChatMembersGetter(self.client, self.config).GetAll(chat).GetByUsername(user.username)
        if chat_members is None:
            return False

        # Get single payment
        single_payment = self.__GetSinglePayment(user)
        # If the user is not in the payment data, consider payment as expired
        return single_payment.IsExpired() if single_payment is not None else True

    # Get all payments
    def __GetAllPayments(self) -> PaymentsDict:
        # Load only the first time
        if self.payments_cache is None:
            self.payments_cache = self.payments_loader.LoadAll()

        return self.payments_cache

    # Get single payment
    def __GetSinglePayment(self,
                           user: pyrogram.types.User) -> Optional[SinglePayment]:
        # Load only the first time
        if self.single_payment_cache is None or self.single_payment_cache["user_id"] != user.id:
            self.single_payment_cache = {}
            self.single_payment_cache["payment"] = self.payments_loader.LoadSingleByUsername(user.username)
            self.single_payment_cache["user_id"] = user.id

        return self.single_payment_cache["payment"]
