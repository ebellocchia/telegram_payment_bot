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
from typing import Optional

from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentsData, PaymentsDataErrors, SinglePayment


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
    def LoadAll(self) -> PaymentsData:
        """Load all payment data.

        Returns:
            PaymentsData containing all payments
        """

    @abstractmethod
    def LoadSingleByUser(self,
                         user: User) -> Optional[SinglePayment]:
        """Load a single payment by user.

        Args:
            user: User to load payment for

        Returns:
            SinglePayment for the user, or None if not found
        """

    @abstractmethod
    def CheckForErrors(self) -> PaymentsDataErrors:
        """Check for errors in the payment data.

        Returns:
            PaymentsDataErrors containing any errors found
        """

    @staticmethod
    def _ColumnToIndex(col: str) -> int:
        """Convert column letter to zero-based index.

        Args:
            col: Column letter (e.g., 'A', 'B')

        Returns:
            Zero-based column index
        """
        return ord(col) - ord("A")
