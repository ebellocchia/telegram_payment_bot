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

from typing import Optional, Tuple

import openpyxl
import xlrd

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.misc.async_helpers import to_thread
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentsData, PaymentsDataErrors, SinglePayment
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase


class PaymentsExcelLoaderConst:
    """Constants for payment Excel loader class."""

    SHEET_IDX: int = 0


class PaymentsExcelLoader(PaymentsLoaderBase):
    """Loader for payment data from Excel files."""

    async def LoadAll(self) -> PaymentsData:
        """Load all payment data from Excel file.

        Returns:
            PaymentsData containing all payments
        """
        return (await self.__LoadAndCheckAll())[0]

    async def LoadSingleByUser(self,
                               user: User) -> Optional[SinglePayment]:
        """Load a single payment by user from Excel file.

        Args:
            user: User to load payment for

        Returns:
            SinglePayment for the user, or None if not found
        """
        return (await self.LoadAll()).GetByUser(user)

    async def CheckForErrors(self) -> PaymentsDataErrors:
        """Check for errors in the Excel file.

        Returns:
            PaymentsDataErrors containing any errors found
        """
        return (await self.__LoadAndCheckAll())[1]

    async def __LoadAndCheckAll(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load and check all payments from Excel file.

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)

        Raises:
            Exception: If an error occurs while loading the file
        """
        payment_file = self.config.GetValue(BotConfigTypes.PAYMENT_EXCEL_FILE)

        try:
            self.logger.GetLogger().info(f"Loading file '{payment_file}'...")

            if payment_file.lower().endswith(".xlsx"):
                payments_data, payments_data_err = await self.__LoadXlsxFile(payment_file)
            elif payment_file.lower().endswith(".xls"):
                payments_data, payments_data_err = await self.__LoadXlsFile(payment_file)
            else:
                raise ValueError(f"Invalid payment file '{payment_file}'")

            self.logger.GetLogger().info(
                f"File '{payment_file}' successfully loaded, number of rows: {payments_data.Count()}"
            )

            return payments_data, payments_data_err

        except Exception:
            self.logger.GetLogger().exception(f"An error occurred while loading file '{payment_file}'")
            raise

    async def __LoadXlsFile(self,
                            payment_file: str) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load payment data from an Excel sheet (xls).

        Args:
            payment_file: Payment file name

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)
        """
        wb = await to_thread(xlrd.open_workbook, payment_file)
        sheet = wb.sheet_by_index(self.config.GetValue(BotConfigTypes.PAYMENT_WORKSHEET_IDX))

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
                    self._AddPayment(i + 1, payments_data, payments_data_err, email, user, expiration)

        return payments_data, payments_data_err

    async def __LoadXlsxFile(self,
                             payment_file: str) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load payment data from an Excel sheet (xlsx).

        Args:
            payment_file: Payment file name

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)
        """
        wb = await to_thread(openpyxl.load_workbook, payment_file, data_only=True)
        sheet = wb.worksheets[self.config.GetValue(BotConfigTypes.PAYMENT_WORKSHEET_IDX)]

        payments_data = PaymentsData(self.config)
        payments_data_err = PaymentsDataErrors()

        email_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EMAIL_COL)) + 1
        user_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_USER_COL)) + 1
        expiration_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EXPIRATION_COL)) + 1

        for i, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            email = str(row[email_col_idx - 1].value or "").strip()
            user = User.FromString(self.config, str(row[user_col_idx - 1].value or "").strip())
            expiration = row[expiration_col_idx - 1].value

            if user.IsValid():
                self._AddPayment(i, payments_data, payments_data_err, email, user, expiration)

        return payments_data, payments_data_err
