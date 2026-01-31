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

from typing import List

from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.google.google_sheet_opener import GoogleSheetOpener
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.async_helpers import to_thread


class GoogleSheetRowsGetter:
    """Google Sheet rows getter."""

    google_sheet_opener: GoogleSheetOpener

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """
        Constructor.

        Args:
            config: Configuration object
            logger: Logger object
        """
        self.google_sheet_opener = GoogleSheetOpener(config, logger)

    async def GetRows(self,
                      worksheet_idx: int) -> List[List[str]]:
        """
        Get all rows from a worksheet.

        Args:
            worksheet_idx: Worksheet index

        Returns:
            List of rows, where each row is a list of strings
        """
        worksheet = await self.google_sheet_opener.OpenWorksheet(worksheet_idx)
        return await to_thread(
            worksheet.get_all_values,
            include_tailing_empty_rows=False,
            include_tailing_empty=False,
            returnas="matrix"
        )
