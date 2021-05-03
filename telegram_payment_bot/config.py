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
from typing import Any
from enum import Enum, auto, unique


#
# Enumerations
#

# Configuration types
@unique
class ConfigTypes(Enum):
    SESSION_NAME = auto(),
    # App
    APP_TEST_MODE = auto(),
    # Users
    AUTHORIZED_USERS = auto(),
    # Support
    SUPPORT_EMAIL = auto(),
    SUPPORT_TELEGRAM = auto(),
    # Payment
    PAYMENT_WEBSITE = auto(),
    PAYMENT_CHECK_PERIOD_SEC = auto(),
    PAYMENT_CHECK_CHAT_IDS = auto()
    PAYMENT_TYPE = auto(),
    PAYMENT_EXCEL_FILE = auto(),
    PAYMENT_GOOGLE_SHEET_ID = auto(),
    PAYMENT_GOOGLE_CRED = auto(),
    PAYMENT_GOOGLE_PICKLE = auto(),
    PAYMENT_EMAIL_COL = auto(),
    PAYMENT_USERNAME_COL = auto(),
    PAYMENT_EXPIRATION_COL = auto(),
    # Email
    EMAIL_ENABLED = auto(),
    EMAIL_FROM = auto(),
    EMAIL_REPLY_TO = auto(),
    EMAIL_HOST = auto(),
    EMAIL_USER = auto(),
    EMAIL_PASSWORD = auto(),
    EMAIL_SUBJECT = auto(),
    EMAIL_ALT_BODY = auto(),
    EMAIL_ALT_BODY_FILE = auto(),
    EMAIL_HTML_BODY = auto(),
    EMAIL_HTML_BODY_FILE = auto(),
    # Logging
    LOG_LEVEL = auto(),
    LOG_CONSOLE_ENABLED = auto(),
    LOG_FILE_ENABLED = auto(),
    LOG_FILE_NAME = auto(),
    LOG_FILE_APPEND = auto(),
    LOG_FILE_MAX_BYTES = auto(),
    LOG_FILE_BACKUP_CNT = auto(),


#
# Classes
#

# Configuration class
class Config:
    # Constructor
    def __init__(self) -> None:
        self.config = {}

    # Get value
    def GetValue(self,
                 config_type: ConfigTypes) -> Any:
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("Config type is not an enumerative of ConfigTypes")

        return self.config[config_type]

    # Set value
    def SetValue(self,
                 config_type: ConfigTypes,
                 value: Any) -> None:
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("Config type is not an enumerative of ConfigTypes")

        self.config[config_type] = value
