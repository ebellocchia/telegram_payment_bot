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
from datetime import datetime
from typing import Optional, Tuple
from telegram_payment_bot.config import ConfigTypes
from telegram_payment_bot.google_sheet_service import GoogleSheetService
from telegram_payment_bot.google_sheet_reader import GoogleSheetReader
from telegram_payment_bot.payments_loader_base import PaymentsLoaderBase
from telegram_payment_bot.payments_data import PaymentErrorTypes, SinglePayment, PaymentsData, PaymentsDataErrors


#
# Classes
#

# Payments Google Sheet loader class
class PaymentsGoogleSheetLoader(PaymentsLoaderBase):
    # Load all payments
    def LoadAll(self) -> PaymentsData:
        return self.__LoadAndCheckAll()[0]

    # Load single payment by username
    def LoadSingleByUsername(self,
                             username: str) -> Optional[SinglePayment]:
        return self.LoadAll().GetByUsername(username)

    # Check for errors
    def CheckForErrors(self) -> PaymentsDataErrors:
        return self.__LoadAndCheckAll()[1]

    # Load and check all payments
    def __LoadAndCheckAll(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        # Get payment sheet ID
        sheet_id = self.config.GetValue(ConfigTypes.PAYMENT_GOOGLE_SHEET_ID)
        cred_file = self.config.GetValue(ConfigTypes.PAYMENT_GOOGLE_CRED)
        pickle_file = self.config.GetValue(ConfigTypes.PAYMENT_GOOGLE_PICKLE)

        try:
            # Log
            self.logger.GetLogger().info("Credential file: %s" % cred_file)
            self.logger.GetLogger().info("Pickle file: %s" % pickle_file)
            self.logger.GetLogger().info("Loading Google Sheet ID \"%s\"..." % sheet_id)

            # Create service
            gs_service = GoogleSheetService()
            gs_service.Init(cred_file, pickle_file)
            # Create reader
            gs_reader = GoogleSheetReader(gs_service, sheet_id)
            # Load sheet
            payments_data, payments_data_err = self.__LoadSheet(gs_reader)

            # Log
            self.logger.GetLogger().info("Google Sheet ID \"%s\" successfully loaded, number of rows: %d" %
                                         (sheet_id, payments_data.Count()))

            return payments_data, payments_data_err

        # Catch everything and log exception
        except Exception:
            self.logger.GetLogger().exception("An error occurred while loading Google Sheet ID \"%s\"" % sheet_id)
            raise

    # Load sheet
    def __LoadSheet(self,
                    gs_reader: GoogleSheetReader) -> Tuple[PaymentsData, PaymentsDataErrors]:
        payments_data = PaymentsData()
        payments_data_err = PaymentsDataErrors()

        # Get column indexes
        email_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EMAIL_COL)
        username_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_USERNAME_COL)
        expiration_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EXPIRATION_COL)

        # Read each row
        last_col = chr(ord('A') + max(email_col_idx, username_col_idx, expiration_col_idx))
        rows = gs_reader.GetRange("A1:" + last_col + "10000")
        for i, row in enumerate(rows):
            # Skip header (first row)
            if i > 0:
                try:
                    # Get cell values
                    email = row[email_col_idx].strip()
                    username = row[username_col_idx].strip()
                    expiration = row[expiration_col_idx].strip()
                except IndexError:
                    self.logger.GetLogger().warning("Row index %d is not valid (some fields are missing), skipping it..." % i)
                else:
                    # Skip empty usernames
                    if username != "":
                        self.__AddPayment(i, payments_data, payments_data_err, email, username, expiration)

        return payments_data, payments_data_err

    # Add payment
    def __AddPayment(self,
                     row_idx: int,
                     payments: PaymentsData,
                     payments_data_err: PaymentsDataErrors,
                     email: str,
                     username: str,
                     expiration: str) -> None:
        # Convert date to datetime object
        try:
            expiration_datetime = datetime.strptime(expiration,
                                                    self.config.GetValue(ConfigTypes.PAYMENT_DATE_FORMAT))
        except ValueError:
            self.logger.GetLogger().warning("Expiration date for username @%s at row %d is not valid (%s), skipped" % (
                username, row_idx, expiration))
            # Add error
            payments_data_err.AddPaymentError(PaymentErrorTypes.INVALID_DATE_ERR,
                                              row_idx + 1,
                                              username,
                                              expiration)
            return

        # Add data
        if payments.AddPayment(email, username, expiration_datetime):
            self.logger.GetLogger().debug("%3d - Row %3d | %s | %s | %s" % (
                payments.Count(), row_idx, email, username, expiration_datetime.date()))
        else:
            self.logger.GetLogger().warning("Username @%s is present more than one time at row %d, skipped" % (
                username, row_idx))
            # Add error
            payments_data_err.AddPaymentError(PaymentErrorTypes.DUPLICATED_USERNAME_ERR,
                                              row_idx + 1,
                                              username)
