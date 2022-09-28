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
from __future__ import annotations

import datetime
from enum import Enum, auto, unique
from typing import Optional

from telegram_payment_bot.bot.bot_config import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.utils.wrapped_dict import WrappedDict
from telegram_payment_bot.utils.wrapped_list import WrappedList


#
# Enumerations
#

# Payment error types
@unique
class PaymentErrorTypes(Enum):
    DUPLICATED_DATA_ERR = auto()
    INVALID_DATE_ERR = auto()


#
# Classes
#

# Single payment class
class SinglePayment:

    email: str
    user: User
    expiration_date: datetime.date

    # Constructor
    def __init__(self,
                 email: str,
                 user: User,
                 expiration_date: datetime.date):
        self.email = email
        self.user = user
        self.expiration_date = expiration_date

    # Get email
    def Email(self) -> str:
        return self.email

    # Get user
    def User(self) -> User:
        return self.user

    # Get expiration date
    def ExpirationDate(self) -> datetime.date:
        return self.expiration_date

    # Get days left until expiration
    def DaysLeft(self) -> int:
        return (self.expiration_date - datetime.date.today()).days

    # Get if expired
    def IsExpired(self) -> bool:
        return self.expiration_date < datetime.date.today()

    # Get if expiring in the specified number of days
    def IsExpiringInDays(self,
                         days: int) -> bool:
        return self.DaysLeft() < days

    # Convert to string
    def ToString(self) -> str:
        return f"{self.email} ({self.user}): {self.expiration_date.strftime('%Y-%m-%d')}"

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Payment error class
class PaymentError:

    err_type: PaymentErrorTypes
    row: int
    user: User
    expiration_date: Optional[str]

    # Constructor
    def __init__(self,
                 err_type: PaymentErrorTypes,
                 row: int,
                 user: User,
                 expiration_data: Optional[str]):
        self.err_type = err_type
        self.row = row
        self.user = user
        self.expiration_date = expiration_data

    # Get type
    def Type(self) -> PaymentErrorTypes:
        return self.err_type

    # Get row
    def Row(self) -> int:
        return self.row

    # Get user
    def User(self) -> User:
        return self.user

    # Get expiration date
    def ExpirationDate(self) -> Optional[str]:
        return self.expiration_date


# Payments data error class
class PaymentsDataErrors(WrappedList):
    # Add payment error
    def AddPaymentError(self,
                        err_type: PaymentErrorTypes,
                        row: int,
                        user: User,
                        expiration: Optional[str] = None) -> None:
        self.AddSingle(PaymentError(err_type, row, user, expiration))


# Payments data class
class PaymentsData(WrappedDict):

    config: ConfigObject

    # Constructor
    def __init__(self,
                 config: ConfigObject) -> None:
        super().__init__()
        self.config = config

    # Add payment
    def AddPayment(self,
                   email: str,
                   user: User,
                   expiration: datetime.date) -> bool:
        # User shall not be existent
        if not self.IsUserExistent(user):
            # Check for duplicated email if configured
            if self.config.GetValue(BotConfigTypes.PAYMENT_CHECK_DUP_EMAIL):
                if email != "" and self.IsEmailExistent(email):
                    return False
            self.AddSingle(user.GetAsKey(), SinglePayment(email, user, expiration))
            return True

        return False

    # Get by email
    def GetByEmail(self,
                   email: str) -> Optional[SinglePayment]:
        for _, payment in self.dict_elements.items():
            if email == payment.Email():
                return payment
        return None

    # Get by user
    def GetByUser(self,
                  user: User) -> Optional[SinglePayment]:
        if not user.IsValid() or user.GetAsKey() not in self.dict_elements:
            return None
        return self.dict_elements[user.GetAsKey()]

    # Get if email is existent
    def IsEmailExistent(self,
                        email: str) -> bool:
        return self.GetByEmail(email) is not None

    # Get if user is existent
    def IsUserExistent(self,
                       user: User) -> bool:
        return self.GetByUser(user) is not None

    # Get if the payment associated to the user is expired
    def IsExpiredByUser(self,
                        user: User) -> bool:
        # Get user payment
        payment = self.GetByUser(user)
        # If user is not in the file, consider it as expired
        return payment.IsExpired() if payment is not None else True

    # Get if the payment associated to the user is expiring payments in the specified number of days
    def IsExpiringInDaysByUser(self,
                               user: User,
                               days: int) -> bool:
        # Get user payment
        payment = self.GetByUser(user)
        # If user is not in the file, consider it as expired
        return payment.IsExpiringInDays(days) if payment is not None else True

    # Filter expired payments
    def FilterExpired(self) -> PaymentsData:
        expired_payments = {user: payment for (user, payment)
                            in self.dict_elements.items()
                            if payment.IsExpired()}

        payments = PaymentsData(self.config)
        payments.AddMultiple(expired_payments)

        return payments

    # Filter expiring payments in the specified number of days
    def FilterExpiringInDays(self,
                             days: int) -> PaymentsData:
        expiring_payments = {user: payment for (user, payment)
                             in self.dict_elements.items()
                             if payment.IsExpiringInDays(days)}

        payments = PaymentsData(self.config)
        payments.AddMultiple(expiring_payments)

        return payments

    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [f"- {str(payment)}" for _, payment in self.dict_elements.items()]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()
