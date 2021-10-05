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
from enum import Enum, auto, unique
from typing import Optional
from datetime import datetime
from telegram_payment_bot.wrapped_dict import WrappedDict
from telegram_payment_bot.wrapped_list import WrappedList


#
# Enumerations
#

# Payment error types
@unique
class PaymentErrorTypes(Enum):
    DUPLICATED_USERNAME_ERR = auto()
    INVALID_DATE_ERR = auto()


#
# Classes
#

# Single payment class
class SinglePayment:
    # Constructor
    def __init__(self,
                 email: str,
                 username: str,
                 expiration_date: datetime):
        self.email = email
        self.username = username
        self.expiration_date = expiration_date

    # Get email
    def Email(self) -> str:
        return self.email

    # Get username
    def Username(self) -> str:
        return self.username

    # Get expiration date
    def ExpirationDate(self) -> datetime:
        return self.expiration_date

    # Get days left until expiration
    def DaysLeft(self) -> int:
        return (self.expiration_date - datetime.now()).days

    # Get if expired
    def IsExpired(self) -> bool:
        return self.expiration_date.date() < datetime.now().date()

    # Get if expiring in the specified number of days
    def IsExpiringInDays(self,
                         days: int) -> bool:
        return self.DaysLeft() < days

    # Convert to string
    def ToString(self) -> str:
        return f"{self.email} (@{self.username}): {self.expiration_date.date().strftime('%d/%m/%Y')}"

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Payment error class
class PaymentError:
    # Constructor
    def __init__(self,
                 err_type: PaymentErrorTypes,
                 row: int,
                 username: str,
                 expiration_data: Optional[str]):
        self.err_type = err_type
        self.row = row
        self.username = username
        self.expiration_date = expiration_data

    # Get type
    def Type(self) -> PaymentErrorTypes:
        return self.err_type

    # Get row
    def Row(self) -> int:
        return self.row

    # Get username
    def Username(self) -> str:
        return self.username

    # Get expiration date
    def ExpirationDate(self) -> Optional[str]:
        return self.expiration_date


# Payments data error class
class PaymentsDataErrors(WrappedList):
    # Add payment error
    def AddPaymentError(self,
                        err_type: PaymentErrorTypes,
                        row: int,
                        username: str,
                        expiration: Optional[str] = None) -> None:
        self.AddSingle(PaymentError(err_type, row, username, expiration))


# Payments data class
class PaymentsData(WrappedDict):
    # Add payment
    def AddPayment(self,
                   email: str,
                   username: str,
                   expiration: datetime) -> bool:
        added = False

        if not self.IsUsernameExistent(username):
            self.AddSingle(username.lower(), SinglePayment(email, username, expiration))
            added = True

        return added

    # Get by username
    def GetByUsername(self,
                      username: str) -> Optional[SinglePayment]:
        try:
            return self.dict_elements[username.lower()]
        except KeyError:
            return None

    # Get if username is existent
    def IsUsernameExistent(self,
                           username: str) -> bool:
        return self.GetByUsername(username) is not None

    # Get if the payment associated to the username is expired
    def IsExpiredByUsername(self,
                            username: str) -> bool:
        # Get user payment
        payment = self.GetByUsername(username)
        # If username is not in the file, consider it as expired
        return payment.IsExpired() if payment is not None else True

    # Get if the payment associated to the username is expiring payments in the specified number of days
    def IsExpiringInDaysByUsername(self,
                                   username: str,
                                   days: int) -> bool:
        # Get user payment
        payment = self.GetByUsername(username)
        # If username is not in the file, consider it as expired
        return payment.IsExpiringInDays(days) if payment is not None else True

    # Filter expired payments
    def FilterExpired(self) -> PaymentsData:
        expired_payments = {username: payment for (username, payment)
                            in self.dict_elements.items()
                            if payment.IsExpired()}

        payments = PaymentsData()
        payments.AddMultiple(expired_payments)

        return payments

    # Filter expiring payments in the specified number of days
    def FilterExpiringInDays(self,
                             days: int) -> PaymentsData:
        expiring_payments = {username: payment for (username, payment)
                             in self.dict_elements.items()
                             if payment.IsExpiringInDays(days)}

        payments = PaymentsData()
        payments.AddMultiple(expiring_payments)

        return payments

    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [f"- {str(payment)}" for (_, payment) in self.dict_elements.items()]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()
