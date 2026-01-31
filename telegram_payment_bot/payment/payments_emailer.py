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
from telegram_payment_bot.email.subscription_emailer import SubscriptionEmailer
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_payment_getter import MembersPaymentGetter
from telegram_payment_bot.payment.payments_data import PaymentsData


class PaymentsEmailerConst:
    """Constants for payments emailer class."""

    SEND_EMAIL_SLEEP_TIME_SEC: float = 0.05


class PaymentsEmailer:
    """Payments emailer class."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    emailer: SubscriptionEmailer
    members_payment_getter: MembersPaymentGetter

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """Constructor."""
        self.client = client
        self.config = config
        self.logger = logger
        self.emailer = SubscriptionEmailer(config)
        self.members_payment_getter = MembersPaymentGetter(client, config, logger)

    async def EmailAllWithExpiredPayment(self) -> PaymentsData:
        """Email all users with expired payment."""
        expired_payments = await self.members_payment_getter.GetAllEmailsWithExpiredPayment()
        await self.__SendEmails(expired_payments)
        return expired_payments

    async def EmailAllWithExpiringPayment(self,
                                          days: int) -> PaymentsData:
        """Email all users with expiring payment in the specified number of days."""
        expired_payments = await self.members_payment_getter.GetAllEmailsWithExpiringPayment(days)
        await self.__SendEmails(expired_payments)
        return expired_payments

    async def __SendEmails(self,
                           expired_payments: PaymentsData) -> None:
        """Send emails to expired payments."""
        if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            self.logger.GetLogger().info("Test mode ON: no email was sent")
            return

        if expired_payments.Any():
            emails = set()
            await self.emailer.Connect()

            for payment in expired_payments.Values():
                pay_email = payment.Email()

                if pay_email == "":
                    self.logger.GetLogger().warning(f"No email set for user {payment.User()}, skipped")
                    continue
                if pay_email in emails:
                    self.logger.GetLogger().warning(f"Email {pay_email} is present more than one time, skipped")
                    continue

                self.emailer.PrepareMsg(pay_email)
                await self.emailer.Send()
                self.logger.GetLogger().info(
                    f"Email successfully sent to: {pay_email} ({payment.User()})"
                )
                emails.add(payment.Email())
                await asyncio.sleep(PaymentsEmailerConst.SEND_EMAIL_SLEEP_TIME_SEC)

            await self.emailer.Disconnect()
