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
from abc import ABC, abstractmethod
from typing import Optional
from telegram_payment_bot.config.configurable_object import ConfigurableObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import SinglePayment, PaymentsData, PaymentsDataErrors


#
# Classes
#

# Payments loader base class
class PaymentsLoaderBase(ABC):

    config: ConfigurableObject
    logger: Logger

    # Constructor
    def __init__(self,
                 config: ConfigurableObject,
                 logger: Logger) -> None:
        self.config = config
        self.logger = logger

    # Load all payments
    @abstractmethod
    def LoadAll(self) -> PaymentsData:
        pass

    # Load single payment by user
    def LoadSingleByUser(self,
                         user: User) -> Optional[SinglePayment]:
        pass

    # Check for errors
    @abstractmethod
    def CheckForErrors(self) -> PaymentsDataErrors:
        pass

    # Convert column string to index
    @staticmethod
    def _ColumnToIndex(col: str) -> int:
        return ord(col) - ord("A")
