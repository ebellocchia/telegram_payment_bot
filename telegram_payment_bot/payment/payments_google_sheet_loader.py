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

import pygsheets

from telegram_payment_bot.bot.bot_config import BotConfigTypes
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import (
    PaymentErrorTypes, PaymentsData, PaymentsDataErrors, SinglePayment
)
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase


#
# Classes
#

# Payments Google Sheet loader class
class PaymentsGoogleSheetLoader(PaymentsLoaderBase):
    # Load all payments
    def LoadAll(self) -> PaymentsData:
        return self.__LoadAndCheckAll()[0]

    # Load single payment by user
    def LoadSingleByUser(self,
                         user: User) -> Optional[SinglePayment]:
        return self.LoadAll().GetByUser(user)

    # Check for errors
    def CheckForErrors(self) -> PaymentsDataErrors:
        return self.__LoadAndCheckAll()[1]

    # Load and check all payments
    def __LoadAndCheckAll(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        # Get configuration
        sheet_id = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_SHEET_ID)
        cred_file = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_CRED)
        cred_path = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_CRED_PATH)

        try:
            # Log
            self.logger.GetLogger().info(f"Credential file: {cred_file}")
            self.logger.GetLogger().info(f"Credential path: {cred_path}")
            self.logger.GetLogger().info(f"Loading Google Sheet ID \"{sheet_id}\"...")

            # Get access to the Google Sheet
            google_client = pygsheets.authorize(client_secret=cred_file, credentials_directory=cred_path)
            google_sheet = google_client.open_by_key(sheet_id)
            worksheet = google_sheet[0]

            # Load worksheet
            payments_data, payments_data_err = self.__LoadWorkSheet(worksheet)

            # Log
            self.logger.GetLogger().info(
                f"Google Sheet ID \"{sheet_id}\" successfully loaded, number of rows: {payments_data.Count()}"
            )

            return payments_data, payments_data_err

        # Catch everything and log exception
        except Exception:
            self.logger.GetLogger().exception(f"An error occurred while loading Google Sheet ID \"{sheet_id}\"")
            raise

    # Load wotksheet
    def __LoadWorkSheet(self,
                        worksheet: pygsheets.Worksheet) -> Tuple[PaymentsData, PaymentsDataErrors]:
        payments_data = PaymentsData(self.config)
        payments_data_err = PaymentsDataErrors()

        # Get column indexes
        email_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EMAIL_COL))
        user_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_USER_COL))
        expiration_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EXPIRATION_COL))

        # Read each row
        rows = worksheet.get_all_values(returnas="matrix")
        for i, row in enumerate(rows):
            # Skip header (first row)
            if i > 0:
                try:
                    # Get cell values
                    email = row[email_col_idx].strip()
                    user = User.FromString(self.config, row[user_col_idx].strip())
                    expiration = row[expiration_col_idx].strip()
                except IndexError:
                    self.logger.GetLogger().warning(
                        f"Row index {i + 1} is not valid (some fields are missing), skipping it..."
                    )
                else:
                    # Skip invalid users
                    if user.IsValid():
                        self.__AddPayment(i + 1, payments_data, payments_data_err, email, user, expiration)

        return payments_data, payments_data_err

    # Add payment
    def __AddPayment(self,
                     row_idx: int,
                     payments_data: PaymentsData,
                     payments_data_err: PaymentsDataErrors,
                     email: str,
                     user: User,
                     expiration: str) -> None:
        # Convert date to datetime object
        try:
            expiration_datetime = datetime.strptime(expiration,
                                                    self.config.GetValue(BotConfigTypes.PAYMENT_DATE_FORMAT)).date()
        except ValueError:
            self.logger.GetLogger().warning(
                f"Expiration date for user {user} at row {row_idx} is not valid ({expiration}), skipped"
            )
            # Add error
            payments_data_err.AddPaymentError(PaymentErrorTypes.INVALID_DATE_ERR,
                                              row_idx,
                                              user,
                                              expiration)
            return

        # Add data
        if payments_data.AddPayment(email, user, expiration_datetime):
            self.logger.GetLogger().debug(
                f"{payments_data.Count():4d} - Row {row_idx:4d} | {email} | {user} | {expiration_datetime}"
            )
        else:
            self.logger.GetLogger().warning(
                f"Row {row_idx} contains duplicated data, skipped"
            )
            # Add error
            payments_data_err.AddPaymentError(PaymentErrorTypes.DUPLICATED_DATA_ERR,
                                              row_idx,
                                              user)
