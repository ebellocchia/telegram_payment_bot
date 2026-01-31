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

import logging
from reprlib import Repr

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.config.config_typing import ConfigSectionsType
from telegram_payment_bot.email.emailer_auth_types import EmailerAuthenticationTypes
from telegram_payment_bot.google.google_cred_types import GoogleCredTypes
from telegram_payment_bot.payment.payment_types import PaymentTypes
from telegram_payment_bot.utils.key_value_converter import KeyValueConverter
from telegram_payment_bot.utils.utils import Utils


class _BotConfigUtils:
    """Utility functions for bot configuration."""

    COL_MIN_VAL: str = "A"
    COL_MAX_VAL: str = "Z"

    @staticmethod
    def Repr(val, max_string=100):
        r = Repr()
        r.maxstring = max_string
        return r.repr(val)

    @staticmethod
    def ReadFile(file_name: str) -> str:
        """
        Read file contents.

        Args:
            file_name: File name to read

        Returns:
            File contents as string
        """
        with open(file_name, encoding="utf-8") as fin:
            return fin.read()

    @staticmethod
    def AreColumnIndexesValid(config: ConfigObject,
                              curr_col: str) -> bool:
        """
        Check if column indexes are valid.

        Args:
            config: Configuration object
            curr_col: Current column to validate

        Returns:
            True if column indexes are valid, False otherwise
        """
        if len(curr_col) != 1 or curr_col < _BotConfigUtils.COL_MIN_VAL or curr_col > _BotConfigUtils.COL_MAX_VAL:
            return False

        columns = []
        for column in (BotConfigTypes.PAYMENT_EMAIL_COL, BotConfigTypes.PAYMENT_USER_COL, BotConfigTypes.PAYMENT_EXPIRATION_COL):
            if config.IsValueSet(column):
                columns.append(config.GetValue(column))

        if len(columns) > 0:
            for col in columns:
                if curr_col == col:
                    return False
        return True


LoggingLevelConverter = KeyValueConverter(
    {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
)


BotConfig: ConfigSectionsType = {
    "pyrogram": [
        {
            "type": BotConfigTypes.API_ID,
            "name": "api_id",
        },
        {
            "type": BotConfigTypes.API_HASH,
            "name": "api_hash",
        },
        {
            "type": BotConfigTypes.BOT_TOKEN,
            "name": "bot_token",
        },
        {
            "type": BotConfigTypes.SESSION_NAME,
            "name": "session_name",
        },
    ],
    "app": [
        {
            "type": BotConfigTypes.APP_TEST_MODE,
            "name": "app_test_mode",
            "conv_fct": Utils.StrToBool,
        },
        {
            "type": BotConfigTypes.APP_LANG_FILE,
            "name": "app_lang_file",
            "def_val": None,
        },
    ],
    "users": [
        {
            "type": BotConfigTypes.AUTHORIZED_USERS,
            "name": "authorized_users",
            "conv_fct": lambda val: val.split(","),
        },
    ],
    "support": [
        {
            "type": BotConfigTypes.SUPPORT_EMAIL,
            "name": "support_email",
            "def_val": "",
        },
        {
            "type": BotConfigTypes.SUPPORT_TELEGRAM,
            "name": "support_telegram",
            "def_val": "",
        },
    ],
    "payment": [
        {
            "type": BotConfigTypes.PAYMENT_WEBSITE,
            "name": "payment_website",
            "def_val": "",
        },
        {
            "type": BotConfigTypes.PAYMENT_CHECK_ON_JOIN,
            "name": "payment_check_on_join",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.PAYMENT_CHECK_DUP_EMAIL,
            "name": "payment_check_dup_email",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.PAYMENT_TYPE,
            "name": "payment_type",
            "conv_fct": lambda val: PaymentTypes[val.upper()],
            "print_fct": lambda val: val.name.upper(),
        },
        {
            "type": BotConfigTypes.PAYMENT_EXCEL_FILE,
            "name": "payment_excel_file",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.PAYMENT_TYPE) == PaymentTypes.EXCEL_FILE,
        },
        {
            "type": BotConfigTypes.PAYMENT_GOOGLE_SHEET_ID,
            "name": "payment_google_sheet_id",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
        },
        {
            "type": BotConfigTypes.PAYMENT_GOOGLE_CRED_TYPE,
            "name": "payment_google_cred_type",
            "def_val": GoogleCredTypes.OAUTH2,
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
            "conv_fct": lambda val: GoogleCredTypes[val.upper()],
            "print_fct": lambda val: val.name.upper(),
        },
        {
            "type": BotConfigTypes.PAYMENT_GOOGLE_CRED,
            "name": "payment_google_cred",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
        },
        {
            "type": BotConfigTypes.PAYMENT_GOOGLE_CRED_PATH,
            "name": "payment_google_cred_path",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
        },
        {
            "type": BotConfigTypes.PAYMENT_USE_USER_ID,
            "name": "payment_use_user_id",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": BotConfigTypes.PAYMENT_WORKSHEET_IDX,
            "name": "payment_worksheet_idx",
            "conv_fct": Utils.StrToInt,
            "def_val": 0,
            "valid_if": lambda cfg, val: val >= 0,
        },
        {
            "type": BotConfigTypes.PAYMENT_EMAIL_COL,
            "name": "payment_email_col",
            "conv_fct": lambda val: val.upper(),
            "def_val": "A",
            "valid_if": _BotConfigUtils.AreColumnIndexesValid,
        },
        {
            "type": BotConfigTypes.PAYMENT_USER_COL,
            "name": "payment_user_col",
            "conv_fct": lambda val: val.upper(),
            "def_val": "B",
            "valid_if": _BotConfigUtils.AreColumnIndexesValid,
        },
        {
            "type": BotConfigTypes.PAYMENT_EXPIRATION_COL,
            "name": "payment_expiration_col",
            "conv_fct": lambda val: val.upper(),
            "def_val": "C",
            "valid_if": _BotConfigUtils.AreColumnIndexesValid,
        },
        {
            "type": BotConfigTypes.PAYMENT_DATE_FORMAT,
            "name": "payment_date_format",
            "def_val": "%d/%m/%Y",
        },
    ],
    "email": [
        {
            "type": BotConfigTypes.EMAIL_ENABLED,
            "name": "email_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": BotConfigTypes.EMAIL_AUTH_TYPE,
            "name": "email_auth_type",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
            "conv_fct": lambda val: EmailerAuthenticationTypes[val.upper()],
            "print_fct": lambda val: val.name.upper(),
        },
        {
            "type": BotConfigTypes.EMAIL_FROM,
            "name": "email_from",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_REPLY_TO,
            "name": "email_reply_to",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_HOST,
            "name": "email_host",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_USER,
            "name": "email_user",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_PASSWORD,
            "name": "email_password",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_SUBJECT,
            "name": "email_subject",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_ALT_BODY,
            "name": "email_alt_body",
            "conv_fct": _BotConfigUtils.ReadFile,
            "print_fct": lambda val: _BotConfigUtils.Repr(val),
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": BotConfigTypes.EMAIL_HTML_BODY,
            "name": "email_html_body",
            "conv_fct": _BotConfigUtils.ReadFile,
            "print_fct": lambda val: _BotConfigUtils.Repr(val),
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.EMAIL_ENABLED),
        },
    ],
    "logging": [
        {
            "type": BotConfigTypes.LOG_LEVEL,
            "name": "log_level",
            "conv_fct": LoggingLevelConverter.KeyToValue,
            "print_fct": LoggingLevelConverter.ValueToKey,
            "def_val": logging.INFO,
        },
        {
            "type": BotConfigTypes.LOG_CONSOLE_ENABLED,
            "name": "log_console_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.LOG_FILE_ENABLED,
            "name": "log_file_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": BotConfigTypes.LOG_FILE_NAME,
            "name": "log_file_name",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": BotConfigTypes.LOG_FILE_USE_ROTATING,
            "name": "log_file_use_rotating",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": BotConfigTypes.LOG_FILE_APPEND,
            "name": "log_file_append",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: (
                cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and not cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)
            ),
        },
        {
            "type": BotConfigTypes.LOG_FILE_MAX_BYTES,
            "name": "log_file_max_bytes",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
        {
            "type": BotConfigTypes.LOG_FILE_BACKUP_CNT,
            "name": "log_file_backup_cnt",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
    ],
}
