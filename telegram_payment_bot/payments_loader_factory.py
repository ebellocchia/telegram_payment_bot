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
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.payment_types import PaymentTypes
from telegram_payment_bot.payments_loader_base import PaymentsLoaderBase
from telegram_payment_bot.payments_excel_loader import PaymentsExcelLoader
from telegram_payment_bot.payments_google_sheet_loader import PaymentsGoogleSheetLoader


#
# Classes
#

# Exception in case of payment type error
class PaymentTypeError(Exception):
    pass


# Payments loader factory class
class PaymentsLoaderFactory:

    config: Config
    logger: Logger

    # Constructor
    def __init__(self,
                 config: Config,
                 logger: Logger) -> None:
        self.config = config
        self.logger = logger

    # Create loader
    def CreateLoader(self) -> PaymentsLoaderBase:
        payment_type = self.config.GetValue(ConfigTypes.PAYMENT_TYPE)
        if payment_type == PaymentTypes.EXCEL_FILE:
            return PaymentsExcelLoader(self.config, self.logger)
        if payment_type == PaymentTypes.GOOGLE_SHEET:
            return PaymentsGoogleSheetLoader(self.config, self.logger)

        raise PaymentTypeError(f"Invalid payment type {payment_type}")
