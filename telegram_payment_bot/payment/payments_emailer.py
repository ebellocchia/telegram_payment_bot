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

import pyrogram

from telegram_payment_bot.bot.bot_config import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.email.subscription_emailer import SubscriptionEmailer
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_payment_getter import MembersPaymentGetter
from telegram_payment_bot.payment.payments_data import PaymentsData


#
# Classes
#

# Constants for payments emailer class
class PaymentsEmailerConst:
    # Sleep time for sending emails
    SEND_EMAIL_SLEEP_TIME_SEC: float = 0.05


# Payments emailer class
class PaymentsEmailer:

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    emailer: SubscriptionEmailer
    members_payment_getter: MembersPaymentGetter

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.emailer = SubscriptionEmailer(config)
        self.members_payment_getter = MembersPaymentGetter(client, config, logger)

    # Email all users with expired payment
    def EmailAllWithExpiredPayment(self) -> PaymentsData:
        # Get expired members
        expired_payments = self.members_payment_getter.GetAllEmailsWithExpiredPayment()

        # Send emails
        self.__SendEmails(expired_payments)

        return expired_payments

    # Email all users with expiring payment in the specified number of days
    def EmailAllWithExpiringPayment(self,
                                    days: int) -> PaymentsData:
        # Get expired members
        expired_payments = self.members_payment_getter.GetAllEmailsWithExpiringPayment(days)

        # Send emails
        self.__SendEmails(expired_payments)

        return expired_payments

    # Send emails to expired payments
    def __SendEmails(self,
                     expired_payments: PaymentsData) -> None:
        # Do not send emails if test mode
        if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            self.logger.GetLogger().info("Test mode ON: no email was sent")
            return

        # Email members if any
        if expired_payments.Any():
            emails = set()

            # Connect
            self.emailer.Connect()

            for payment in expired_payments.Values():
                pay_email = payment.Email()

                # Check empty email
                if pay_email == "":
                    self.logger.GetLogger().warning(f"No email set for user {payment.User()}, skipped")
                    continue
                # Check duplicated emails
                if pay_email in emails:
                    self.logger.GetLogger().warning(f"Email {pay_email} is present more than one time, skipped")
                    continue

                # Prepare and send message
                self.emailer.PrepareMsg(pay_email)
                # Send email
                self.emailer.Send()
                self.logger.GetLogger().info(
                    f"Email successfully sent to: {pay_email} ({payment.User()})"
                )
                # Add to set
                emails.add(payment.Email())
                # Sleep
                time.sleep(PaymentsEmailerConst.SEND_EMAIL_SLEEP_TIME_SEC)

            # Disconnect
            self.emailer.Disconnect()
