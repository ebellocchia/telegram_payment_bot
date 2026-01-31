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

from typing import Optional

import pygsheets

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.google.google_cred_types import GoogleCredTypes
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.async_helpers import to_thread


class GoogleSheetOpener:
    """Google Sheet opener."""

    config: ConfigObject
    logger: Logger
    google_sheet: Optional[pygsheets.Spreadsheet]

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """
        Constructor.

        Args:
            config: Configuration object
            logger: Logger object
        """
        self.config = config
        self.logger = logger
        self.google_sheet = None

    async def OpenWorksheet(self,
                            worksheet_idx: int) -> pygsheets.Worksheet:
        """
        Open a worksheet by index.

        Args:
            worksheet_idx: Worksheet index

        Returns:
            The worksheet object
        """
        await self.__OpenGoogleSheet()
        assert self.google_sheet is not None
        return self.google_sheet[worksheet_idx]

    async def __OpenGoogleSheet(self) -> None:
        """Open Google Sheet using configured credentials."""
        if self.google_sheet is not None:
            return

        # Get configuration
        sheet_id = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_SHEET_ID)
        cred_file = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_CRED)
        cred_type = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_CRED_TYPE)

        # Log
        self.logger.GetLogger().info(f"Credential file: {cred_file}")
        self.logger.GetLogger().info(f"Credential type: {cred_type}")
        self.logger.GetLogger().info(f"Opening Google Sheet ID \"{sheet_id}\"...")

        # Authorize and open Google Sheet
        if cred_type == GoogleCredTypes.OAUTH2:
            cred_path = self.config.GetValue(BotConfigTypes.PAYMENT_GOOGLE_CRED_PATH)
            self.logger.GetLogger().info(f"Credential path: {cred_path}")

            google_client = await to_thread(
                pygsheets.authorize,
                client_secret=cred_file,
                credentials_directory=cred_path,
                local=True
            )
        elif cred_type == GoogleCredTypes.SERVICE_ACCOUNT:
            google_client = await to_thread(pygsheets.authorize, service_file=cred_file)
        else:
            raise ValueError("Invalid credential type")

        self.google_sheet = await to_thread(google_client.open_by_key, sheet_id)
