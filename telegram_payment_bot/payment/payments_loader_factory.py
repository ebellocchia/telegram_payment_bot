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

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.payment.payment_types import PaymentTypes
from telegram_payment_bot.payment.payments_excel_loader import PaymentsExcelLoader
from telegram_payment_bot.payment.payments_google_sheet_loader import PaymentsGoogleSheetLoader
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase


class PaymentTypeError(Exception):
    """Exception raised when an invalid payment type is specified."""


class PaymentsLoaderFactory:
    """Factory for creating payments loader instances based on configuration."""

    config: ConfigObject
    logger: Logger

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """Initialize the payments loader factory.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

    def CreateLoader(self) -> PaymentsLoaderBase:
        """Create a payments loader based on the configured payment type.

        Returns:
            PaymentsLoaderBase instance for the configured payment type

        Raises:
            PaymentTypeError: If the payment type is invalid
        """
        payment_type = self.config.GetValue(BotConfigTypes.PAYMENT_TYPE)
        if payment_type == PaymentTypes.EXCEL_FILE:
            return PaymentsExcelLoader(self.config, self.logger)
        if payment_type == PaymentTypes.GOOGLE_SHEET:
            return PaymentsGoogleSheetLoader(self.config, self.logger)

        raise PaymentTypeError(f"Invalid payment type {payment_type}")
