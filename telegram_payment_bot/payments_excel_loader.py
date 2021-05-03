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
import xlrd
from datetime import datetime
from typing import Optional
from telegram_payment_bot.config import ConfigTypes
from telegram_payment_bot.payments_loader_base import PaymentsLoaderBase
from telegram_payment_bot.payments_data import SinglePayment, PaymentsDict


#
# Classes
#

# Constant for payment Excel loader class
class PaymentsExcelLoaderConst:
    # Sheet index
    SHEET_IDX: int = 0


# Payments Excel loader class
class PaymentsExcelLoader(PaymentsLoaderBase):
    # Load all payments
    def LoadAll(self) -> PaymentsDict:
        # Get payment file
        payment_file = self.config.GetValue(ConfigTypes.PAYMENT_EXCEL_FILE)

        try:
            # Log
            self.logger.GetLogger().info("Loading file \"%s\"..." % payment_file)

            # Get sheet
            sheet = self.__GetSheet(payment_file)
            # Load sheet
            payments = self.__LoadSheet(sheet)

            # Log
            self.logger.GetLogger().info("File \"%s\" successfully loaded, number of rows: %d" %
                                         (payment_file, payments.Count()))

            return payments

        # Catch everything and log exception
        except Exception:
            self.logger.GetLogger().exception("An error occurred while loading file \"%s\"" % payment_file)
            raise

    # Load single payment by username
    def LoadSingleByUsername(self,
                             username: str) -> Optional[SinglePayment]:
        return self.LoadAll().GetByUsername(username)

    # Get sheet
    @staticmethod
    def __GetSheet(payment_file: str) -> xlrd.sheet.Sheet:
        # Open file
        wb = xlrd.open_workbook(payment_file)
        return wb.sheet_by_index(PaymentsExcelLoaderConst.SHEET_IDX)

    # Load sheet
    def __LoadSheet(self,
                    sheet: xlrd.sheet.Sheet) -> PaymentsDict:
        payments = PaymentsDict()

        # Get column indexes
        email_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EMAIL_COL)
        username_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_USERNAME_COL)
        expiration_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EXPIRATION_COL)

        # Read each row, skipping the first one (i.e. header)
        for i in range(sheet.nrows):
            # Skip header (first row)
            if i > 0:
                try:
                    # Get cell values
                    email = str(sheet.cell_value(i, email_col_idx)).strip()
                    username = str(sheet.cell_value(i, username_col_idx)).strip()
                    # Convert date to datetime object
                    expiration = sheet.cell_value(i, expiration_col_idx)
                except IndexError:
                    email = ""
                    username = ""
                    expiration = ""
                    self.logger.GetLogger().warning("Row index %d is not valid (some fields are missing), skipping it..." % i)

                # Skip empty usernames
                if username != "":
                    # In Excel, a date can be a date or a string
                    try:
                        expiration_datetime = xlrd.xldate_as_datetime(expiration, 0)
                    except TypeError:
                        try:
                            expiration_datetime = datetime.strptime(expiration.strip(), "%d/%m/%Y")
                        except ValueError:
                            expiration_datetime = datetime.strptime(expiration, "%Y-%m-%d")

                    # Add data
                    payments.AddPayment(email, username, expiration_datetime)
                    # Log
                    self.logger.GetLogger().debug("%3d - Row %3d | %s | %s | %s" % (
                        payments.Count(), i, email, username, expiration_datetime.date()))

        return payments
