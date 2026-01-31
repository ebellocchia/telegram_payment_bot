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

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.google.google_sheet_rows_getter import GoogleSheetRowsGetter
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.user import User
from telegram_payment_bot.payment.payments_data import PaymentsData, PaymentsDataErrors, SinglePayment
from telegram_payment_bot.payment.payments_loader_base import PaymentsLoaderBase


class PaymentsGoogleSheetLoader(PaymentsLoaderBase):
    """Loader for payment data from Google Sheets."""

    google_sheet_rows_getter: GoogleSheetRowsGetter

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """Initialize the Google Sheets payments loader.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        super().__init__(config, logger)
        self.google_sheet_rows_getter = GoogleSheetRowsGetter(config, logger)

    async def LoadAll(self) -> PaymentsData:
        """Load all payment data from Google Sheet.

        Returns:
            PaymentsData containing all payments
        """
        return (await self.__LoadAndCheckAll())[0]

    async def LoadSingleByUser(self,
                               user: User) -> Optional[SinglePayment]:
        """Load a single payment by user from Google Sheet.

        Args:
            user: User to load payment for

        Returns:
            SinglePayment for the user, or None if not found
        """
        return (await self.LoadAll()).GetByUser(user)

    async def CheckForErrors(self) -> PaymentsDataErrors:
        """Check for errors in the Google Sheet.

        Returns:
            PaymentsDataErrors containing any errors found
        """
        return (await self.__LoadAndCheckAll())[1]

    async def __LoadAndCheckAll(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load and check all payments from Google Sheet.

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)

        Raises:
            Exception: If an error occurs while loading the sheet
        """
        try:
            payments_data, payments_data_err = await self.__LoadWorkSheet()
            self.logger.GetLogger().info(
                f"Google Sheet successfully loaded, number of rows: {payments_data.Count()}"
            )
            return payments_data, payments_data_err

        except Exception:
            self.logger.GetLogger().exception("An error occurred while loading Google Sheet")
            raise

    async def __LoadWorkSheet(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        """Load payment data from a Google Sheet.

        Returns:
            Tuple of (PaymentsData, PaymentsDataErrors)
        """
        payments_data = PaymentsData(self.config)
        payments_data_err = PaymentsDataErrors()

        email_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EMAIL_COL))
        user_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_USER_COL))
        expiration_col_idx = self._ColumnToIndex(self.config.GetValue(BotConfigTypes.PAYMENT_EXPIRATION_COL))

        rows = await self.google_sheet_rows_getter.GetRows(
            self.config.GetValue(BotConfigTypes.PAYMENT_WORKSHEET_IDX)
        )

        for i, row in enumerate(rows):
            if i == 0:
                continue

            try:
                email = row[email_col_idx].strip()
                user = User.FromString(self.config, row[user_col_idx].strip())
                expiration = row[expiration_col_idx].strip()
            except IndexError:
                self.logger.GetLogger().warning(
                    f"Row index {i + 1} is not valid (some fields are missing), skipping it..."
                )
            else:
                if user.IsValid():
                    self._AddPayment(i + 1, payments_data, payments_data_err, email, user, expiration)

        return payments_data, payments_data_err
