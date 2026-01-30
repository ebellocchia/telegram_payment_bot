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

from datetime import datetime
from typing import Any, Optional, Tuple

import xlrd

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentErrorTypes, PaymentsData, PaymentsDataErrors, SinglePayment
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase


class PaymentsExcelLoaderConst:
    """Constants for payment Excel loader class."""

    SHEET_IDX: int = 0


class PaymentsExcelLoader(PaymentsLoaderBase):
    """Loader for payment data from Excel files."""

    def LoadAll(self) -> PaymentsData:
        """Load all payment data from Excel file.

        Returns:
            PaymentsData containing all payments
        """
        return self.__LoadAndCheckAll()[0]

    def LoadSingleByUser(self,
                         user: User) -> Optional[SinglePayment]:
        """Load a single payment by user from Excel file.

        Args:
            user: User to load payment for

        Returns:
            SinglePayment for the user, or None if not found
        """
        return self.LoadAll().GetByUser(user)

    def CheckForErrors(self) -> PaymentsDataErrors:
        """Check for errors in the Excel file.

        Returns:
            PaymentsDataErrors containing any errors found
        """
        return self.__LoadAndCheckAll()[1]

    def __LoadAndCheckAll(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load and check all payments from Excel file.

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)

        Raises:
            Exception: If an error occurs while loading the file
        """
        payment_file = self.config.GetValue(BotConfigTypes.PAYMENT_EXCEL_FILE)

        try:
            self.logger.GetLogger().info(f"Loading file \"{payment_file}\"...")

            sheet = self.__GetSheet(payment_file)
            payments_data, payments_data_err = self.__LoadSheet(sheet)

            self.logger.GetLogger().info(
                f"File \"{payment_file}\" successfully loaded, number of rows: {payments_data.Count()}"
            )

            return payments_data, payments_data_err

        except Exception:
            self.logger.GetLogger().exception(f"An error occurred while loading file \"{payment_file}\"")
            raise

    def __LoadSheet(self,
                    sheet: xlrd.sheet.Sheet) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load payment data from an Excel sheet.

        Args:
            sheet: Excel sheet to load from

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)
        """
        payments_data = PaymentsData(self.config)
        payments_data_err = PaymentsDataErrors()

        email_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EMAIL_COL))
        user_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_USER_COL))
        expiration_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EXPIRATION_COL))

        for i in range(sheet.nrows):
            if i > 0:
                email = str(sheet.cell_value(i, email_col_idx)).strip()
                user = User.FromString(self.config, str(sheet.cell_value(i, user_col_idx)).strip())
                expiration = sheet.cell_value(i, expiration_col_idx)

                if user.IsValid():
                    self.__AddPayment(i + 1, payments_data, payments_data_err, email, user, expiration)

        return payments_data, payments_data_err

    def __AddPayment(self,
                     row_idx: int,
                     payments_data: PaymentsData,
                     payments_data_err: PaymentsDataErrors,
                     email: str,
                     user: User,
                     expiration: Any) -> None:
        """Add a payment entry from a row.

        Args:
            row_idx: Row index (1-based)
            payments_data: PaymentsData to add to
            payments_data_err: PaymentsDataErrors to add errors to
            email: Email address
            user: User object
            expiration: Expiration value (number or string)
        """
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
                payments_data_err.AddPaymentError(PaymentErrorTypes.INVALID_DATE_ERR,
                                                  row_idx,
                                                  user,
                                                  expiration)
                return

        if payments_data.AddPayment(email, user, expiration_datetime):
            self.logger.GetLogger().debug(
                f"{payments_data.Count():4d} - Row {row_idx:4d} | {email} | {user} | {expiration_datetime}"
            )
        else:
            self.logger.GetLogger().warning(
                f"Row {row_idx} contains duplicated data, skipped"
            )
            payments_data_err.AddPaymentError(PaymentErrorTypes.DUPLICATED_DATA_ERR,
                                              row_idx,
                                              user)

    def __GetSheet(self,
                   payment_file: str) -> xlrd.sheet.Sheet:
        """Get the Excel sheet from the payment file.

        Args:
            payment_file: Path to the Excel file

        Returns:
            xlrd.sheet.Sheet instance
        """
        wb = xlrd.open_workbook(payment_file)
        return wb.sheet_by_index(self.config.GetValue(BotConfigTypes.PAYMENT_WORKSHEET_IDX))
