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
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.members_payment_getter import MembersPaymentGetter
from telegram_payment_bot.subscription_emailer import SubscriptionEmailer
from telegram_payment_bot.payments_data import PaymentsData


#
# Classes
#

# Constants for payments emailer class
class PaymentsEmailerConst:
    # Sleep time for sending emails
    SEND_EMAIL_SLEEP_TIME_SEC: float = 0.05


# Payments emailer class
class PaymentsEmailer:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
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
        if self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            self.logger.GetLogger().info("Test mode ON: no email was sent")
            return

        # Email members if any
        if expired_payments.Any():
            # Connect
            self.emailer.Connect()

            for username in expired_payments:
                payment = expired_payments.GetByUsername(username)

                if payment.Email() != "":
                    # Prepare and send message
                    self.emailer.PrepareMsg(payment.Email())
                    # Send email
                    self.emailer.Send()
                    self.logger.GetLogger().info("Email successfully sent to: %s (@%s)" %
                                                 (payment.Email(), payment.Username()))
                    # Sleep
                    time.sleep(PaymentsEmailerConst.SEND_EMAIL_SLEEP_TIME_SEC)
                else:
                    self.logger.GetLogger().warning("No email set for user @%s, skipped" % payment.Username())

            # Disconnect
            self.emailer.Disconnect()
