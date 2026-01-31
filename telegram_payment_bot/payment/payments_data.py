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

from __future__ import annotations

import datetime
from enum import Enum, auto, unique
from typing import Optional

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.utils.wrapped_dict import WrappedDict
from telegram_payment_bot.utils.wrapped_list import WrappedList


@unique
class PaymentErrorTypes(Enum):
    """Enumeration of payment error types."""

    DUPLICATED_DATA_ERR = auto()
    INVALID_DATE_ERR = auto()


class SinglePayment:
    """Represents a single payment entry for a user."""

    email: str
    user: User
    expiration_date: datetime.date

    def __init__(self,
                 email: str,
                 user: User,
                 expiration_date: datetime.date):
        """Initialize a single payment entry.

        Args:
            email: User email address
            user: User object
            expiration_date: Payment expiration date
        """
        self.email = email
        self.user = user
        self.expiration_date = expiration_date

    def Email(self) -> str:
        """Get the email address.

        Returns:
            Email address
        """
        return self.email

    def User(self) -> User:
        """Get the user object.

        Returns:
            User object
        """
        return self.user

    def ExpirationDate(self) -> datetime.date:
        """Get the expiration date.

        Returns:
            Expiration date
        """
        return self.expiration_date

    def DaysLeft(self) -> int:
        """Get the number of days left until expiration.

        Returns:
            Number of days left (negative if expired)
        """
        return (self.expiration_date - datetime.date.today()).days

    def IsExpired(self) -> bool:
        """Check if the payment is expired.

        Returns:
            True if expired, False otherwise
        """
        return self.expiration_date < datetime.date.today()

    def IsExpiringInDays(self,
                         days: int) -> bool:
        """Check if the payment is expiring within the specified number of days.

        Args:
            days: Number of days to check

        Returns:
            True if expiring within the specified days, False otherwise
        """
        return self.DaysLeft() < days

    def ToString(self) -> str:
        """Convert to string representation.

        Returns:
            String representation
        """
        if self.email:
            return f"{self.email} ({self.user}): {self.expiration_date.strftime('%Y-%m-%d')}"
        return f"{self.user}: {self.expiration_date.strftime('%Y-%m-%d')}"

    def __str__(self) -> str:
        """Convert to string representation.

        Returns:
            String representation
        """
        return self.ToString()


class PaymentError:
    """Represents an error in payment data."""

    err_type: PaymentErrorTypes
    row: int
    user: User
    expiration_date: Optional[str]

    def __init__(self,
                 err_type: PaymentErrorTypes,
                 row: int,
                 user: User,
                 expiration_data: Optional[str]):
        """Initialize a payment error.

        Args:
            err_type: Type of error
            row: Row number where error occurred
            user: User associated with the error
            expiration_data: Expiration date string (if applicable)
        """
        self.err_type = err_type
        self.row = row
        self.user = user
        self.expiration_date = expiration_data

    def Type(self) -> PaymentErrorTypes:
        """Get the error type.

        Returns:
            Error type
        """
        return self.err_type

    def Row(self) -> int:
        """Get the row number.

        Returns:
            Row number
        """
        return self.row

    def User(self) -> User:
        """Get the user.

        Returns:
            User object
        """
        return self.user

    def ExpirationDate(self) -> Optional[str]:
        """Get the expiration date string.

        Returns:
            Expiration date string, or None
        """
        return self.expiration_date


class PaymentsDataErrors(WrappedList):
    """Collection of payment data errors."""

    def AddPaymentError(self,
                        err_type: PaymentErrorTypes,
                        row: int,
                        user: User,
                        expiration: Optional[str] = None) -> None:
        """Add a payment error to the collection.

        Args:
            err_type: Type of error
            row: Row number where error occurred
            user: User associated with the error
            expiration: Expiration date string (optional)
        """
        self.AddSingle(PaymentError(err_type, row, user, expiration))


class PaymentsData(WrappedDict):
    """Collection of payment data."""

    config: ConfigObject

    def __init__(self,
                 config: ConfigObject) -> None:
        """Initialize payments data collection.

        Args:
            config: Configuration object
        """
        super().__init__()
        self.config = config

    def AddPayment(self,
                   email: str,
                   user: User,
                   expiration: datetime.date) -> bool:
        """Add a payment to the collection.

        Args:
            email: User email address
            user: User object
            expiration: Payment expiration date

        Returns:
            True if added successfully, False if user already exists or email is duplicated
        """
        if not self.IsUserExistent(user):
            if self.config.GetValue(BotConfigTypes.PAYMENT_CHECK_DUP_EMAIL):
                if email != "" and self.IsEmailExistent(email):
                    return False
            self.AddSingle(user.GetAsKey(), SinglePayment(email, user, expiration))
            return True

        return False

    def GetByEmail(self,
                   email: str) -> Optional[SinglePayment]:
        """Get payment by email address.

        Args:
            email: Email address to search for

        Returns:
            SinglePayment if found, None otherwise
        """
        for _, payment in self.dict_elements.items():
            if email == payment.Email():
                return payment
        return None

    def GetByUser(self,
                  user: User) -> Optional[SinglePayment]:
        """Get payment by user.

        Args:
            user: User to search for

        Returns:
            SinglePayment if found, None otherwise
        """
        if not user.IsValid() or user.GetAsKey() not in self.dict_elements:
            return None
        return self.dict_elements[user.GetAsKey()]

    def IsEmailExistent(self,
                        email: str) -> bool:
        """Check if an email exists in the payment data.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        return self.GetByEmail(email) is not None

    def IsUserExistent(self,
                       user: User) -> bool:
        """Check if a user exists in the payment data.

        Args:
            user: User to check

        Returns:
            True if user exists, False otherwise
        """
        return self.GetByUser(user) is not None

    def IsExpiredByUser(self,
                        user: User) -> bool:
        """Check if a user's payment is expired.

        Args:
            user: User to check

        Returns:
            True if expired or user not found, False otherwise
        """
        payment = self.GetByUser(user)
        return payment.IsExpired() if payment is not None else True

    def IsExpiringInDaysByUser(self,
                               user: User,
                               days: int) -> bool:
        """Check if a user's payment is expiring within specified days.

        Args:
            user: User to check
            days: Number of days to check

        Returns:
            True if expiring or user not found, False otherwise
        """
        payment = self.GetByUser(user)
        return payment.IsExpiringInDays(days) if payment is not None else True

    def FilterExpired(self) -> PaymentsData:
        """Filter and return only expired payments.

        Returns:
            PaymentsData containing only expired payments
        """
        expired_payments = {user: payment for (user, payment)
                            in self.dict_elements.items()
                            if payment.IsExpired()}

        payments = PaymentsData(self.config)
        payments.AddMultiple(expired_payments)

        return payments

    def FilterExpiringInDays(self,
                             days: int) -> PaymentsData:
        """Filter and return payments expiring within specified days.

        Args:
            days: Number of days to check

        Returns:
            PaymentsData containing payments expiring within specified days
        """
        expiring_payments = {user: payment for (user, payment)
                             in self.dict_elements.items()
                             if payment.IsExpiringInDays(days)}

        payments = PaymentsData(self.config)
        payments.AddMultiple(expiring_payments)

        return payments

    def ToString(self) -> str:
        """Convert to string representation.

        Returns:
            String representation
        """
        return "\n".join(
            [f"- {str(payment)}" for _, payment in self.dict_elements.items()]
        )

    def __str__(self) -> str:
        """Convert to string representation.

        Returns:
            String representation
        """
        return self.ToString()
