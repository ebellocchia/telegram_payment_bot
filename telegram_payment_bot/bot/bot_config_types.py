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

from enum import auto, unique

from telegram_payment_bot.config.config_object import ConfigTypes


@unique
class BotConfigTypes(ConfigTypes):
    """Bot configuration types enumeration."""

    API_ID = auto()
    API_HASH = auto()
    BOT_TOKEN = auto()
    SESSION_NAME = auto()
    # App
    APP_TEST_MODE = auto()
    APP_LANG_FILE = auto()
    # Users
    AUTHORIZED_USERS = auto()
    # Support
    SUPPORT_EMAIL = auto()
    SUPPORT_TELEGRAM = auto()
    # Payment
    PAYMENT_WEBSITE = auto()
    PAYMENT_CHECK_ON_JOIN = auto()
    PAYMENT_CHECK_DUP_EMAIL = auto()
    PAYMENT_TYPE = auto()
    PAYMENT_EXCEL_FILE = auto()
    PAYMENT_GOOGLE_SHEET_ID = auto()
    PAYMENT_GOOGLE_CRED_TYPE = auto()
    PAYMENT_GOOGLE_CRED = auto()
    PAYMENT_GOOGLE_CRED_PATH = auto()
    PAYMENT_USE_USER_ID = auto()
    PAYMENT_WORKSHEET_IDX = auto()
    PAYMENT_EMAIL_COL = auto()
    PAYMENT_USER_COL = auto()
    PAYMENT_EXPIRATION_COL = auto()
    PAYMENT_DATE_FORMAT = auto()
    # Email
    EMAIL_ENABLED = auto()
    EMAIL_AUTH_TYPE = auto()
    EMAIL_FROM = auto()
    EMAIL_REPLY_TO = auto()
    EMAIL_HOST = auto()
    EMAIL_USER = auto()
    EMAIL_PASSWORD = auto()
    EMAIL_SUBJECT = auto()
    EMAIL_ALT_BODY = auto()
    EMAIL_HTML_BODY = auto()
    # Logging
    LOG_LEVEL = auto()
    LOG_CONSOLE_ENABLED = auto()
    LOG_FILE_ENABLED = auto()
    LOG_FILE_NAME = auto()
    LOG_FILE_USE_ROTATING = auto()
    LOG_FILE_APPEND = auto()
    LOG_FILE_MAX_BYTES = auto()
    LOG_FILE_BACKUP_CNT = auto()
