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

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import xlrd

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentErrorTypes, PaymentsData, PaymentsDataErrors, SinglePayment


class PaymentsLoaderBase(ABC):
    """Base class for payment data loaders."""

    config: ConfigObject
    logger: Logger

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """Initialize the payments loader.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

    @abstractmethod
    async def LoadAll(self) -> PaymentsData:
        """Load all payment data.

        Returns:
            PaymentsData containing all payments
        """

    @abstractmethod
    async def LoadSingleByUser(self,
                               user: User) -> Optional[SinglePayment]:
        """Load a single payment by user.

        Args:
            user: User to load payment for

        Returns:
            SinglePayment for the user, or None if not found
        """

    @abstractmethod
    async def CheckForErrors(self) -> PaymentsDataErrors:
        """Check for errors in the payment data.

        Returns:
            PaymentsDataErrors containing any errors found
        """

    def _AddPayment(self,
                    row_idx: int,
                    payments_data: PaymentsData,
                    payments_data_err: PaymentsDataErrors,
                    email: str,
                    user: User,
                    expiration: str) -> None:
        """Add a payment entry from a row.

        Args:
            row_idx: Row index (1-based)
            payments_data: PaymentsData to add to
            payments_data_err: PaymentsDataErrors to add errors to
            email: Email address
            user: User object
            expiration: Expiration date string
        """
        try:
            if isinstance(expiration, datetime):
                expiration_datetime = expiration.date()
            elif isinstance(expiration, (int, float)):
                expiration_datetime = xlrd.xldate_as_datetime(expiration, 0).date()
            else:
                expiration_datetime = datetime.strptime(expiration.strip(),
                                                        self.config.GetValue(BotConfigTypes.PAYMENT_DATE_FORMAT)).date()
        except (ValueError, AttributeError):
            self.logger.GetLogger().warning(
                f"Expiration date for user {user} at row {row_idx} is not valid ({expiration}), skipped"
            )
            payments_data_err.AddPaymentError(PaymentErrorTypes.INVALID_DATE_ERR,
                                              row_idx,
                                              user,
                                              expiration)
            return

        if payments_data.AddPayment(email, user, expiration_datetime):
            self.logger.GetLogger().debug(
                f"{payments_data.Count():4d} - Row {row_idx:4d} | {email} | {user} | {expiration_datetime}"
            )
        else:
            self.logger.GetLogger().warning(
                f"Row {row_idx} contains duplicated data, skipped"
            )
            payments_data_err.AddPaymentError(PaymentErrorTypes.DUPLICATED_DATA_ERR,
                                              row_idx,
                                              user)

    @staticmethod
    def _ColumnToIndex(col: str) -> int:
        """Convert column letter to zero-based index.

        Args:
            col: Column letter (e.g., 'A', 'B')

        Returns:
            Zero-based column index
        """
        return ord(col) - ord("A")
