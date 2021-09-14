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
from typing import Optional
from datetime import datetime
from telegram_payment_bot.wrapped_dict import WrappedDict


#
# Classes
#

# Single payment class
class SinglePayment:
    # Constructor
    def __init__(self,
                 email: str,
                 username: str,
                 expiration: datetime):
        self.email = email
        self.username = username
        self.expiration = expiration

    # Get email
    def Email(self) -> str:
        return self.email

    # Get username
    def Username(self) -> str:
        return self.username

    # Get expiration
    def Expiration(self) -> datetime:
        return self.expiration

    # Get days left until expiration
    def DaysLeft(self) -> int:
        return (self.expiration - datetime.now()).days

    # Get if expired
    def IsExpired(self) -> bool:
        return self.expiration.date() < datetime.now().date()

    # Get if expiring in the specified number of days
    def IsExpiringInDays(self,
                         days: int) -> bool:
        return self.DaysLeft() < days


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
        return "".join(
            ["- %s (@%s): %s\n" %
             (payment.Email(), payment.Username(), payment.Expiration().date().strftime("%d/%m/%Y"))
             for (_, payment) in self.dict_elements.items()])
