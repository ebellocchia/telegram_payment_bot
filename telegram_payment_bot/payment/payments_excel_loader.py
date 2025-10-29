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
from typing import Any, Optional, Tuple

import xlrd

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentErrorTypes, PaymentsData, PaymentsDataErrors, SinglePayment
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase


#
# Classes
#

# Constants for payment Excel loader class
class PaymentsExcelLoaderConst:
    # Sheet index
    SHEET_IDX: int = 0


# Payments Excel loader class
class PaymentsExcelLoader(PaymentsLoaderBase):
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
        # Get payment file
        payment_file = self.config.GetValue(BotConfigTypes.PAYMENT_EXCEL_FILE)

        try:
            # Log
            self.logger.GetLogger().info(f"Loading file \"{payment_file}\"...")

            # Get sheet
            sheet = self.__GetSheet(payment_file)
            # Load sheet
            payments_data, payments_data_err = self.__LoadSheet(sheet)

            # Log
            self.logger.GetLogger().info(
                f"File \"{payment_file}\" successfully loaded, number of rows: {payments_data.Count()}"
            )

            return payments_data, payments_data_err

        # Catch everything and log exception
        except Exception:
            self.logger.GetLogger().exception(f"An error occurred while loading file \"{payment_file}\"")
            raise

    # Load sheet
    def __LoadSheet(self,
                    sheet: xlrd.sheet.Sheet) -> Tuple[PaymentsData, PaymentsDataErrors]:
        payments_data = PaymentsData(self.config)
        payments_data_err = PaymentsDataErrors()

        # Get column indexes
        email_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EMAIL_COL))
        user_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_USER_COL))
        expiration_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EXPIRATION_COL))

        # Read each row
        for i in range(sheet.nrows):
            # Skip header (first row)
            if i > 0:
                # Get cell values
                email = str(sheet.cell_value(i, email_col_idx)).strip()
                user = User.FromString(self.config, str(sheet.cell_value(i, user_col_idx)).strip())
                expiration = sheet.cell_value(i, expiration_col_idx)

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
                     expiration: Any) -> None:
        # In Excel, a date can be a number or a string
        try:
            expiration_datetime = xlrd.xldate_as_datetime(expiration, 0).date()
        except TypeError:
            try:
                expiration_datetime = datetime.strptime(expiration.strip(),
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

    # Get sheet
    def __GetSheet(self,
                   payment_file: str) -> xlrd.sheet.Sheet:
        # Open file
        wb = xlrd.open_workbook(payment_file)
        return wb.sheet_by_index(self.config.GetValue(BotConfigTypes.PAYMENT_WORKSHEET_IDX))
