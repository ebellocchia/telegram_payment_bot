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
import configparser
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.payment_types import PaymentTypes
from telegram_payment_bot.utils import Utils


#
# Classes
#

# Configuration type converter class
class ConfigTypeConverter:
    # String to payment type
    STR_TO_PAYMENT_TYPE: Dict[str, PaymentTypes] = {
        "EXCEL_FILE": PaymentTypes.EXCEL_FILE,
        "GOOGLE_SHEET": PaymentTypes.GOOGLE_SHEET,
    }

    # String to log level
    STR_TO_LOG_LEVEL: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Convert string to payment type
    @staticmethod
    def StrToPaymentType(payment_type: str) -> PaymentTypes:
        return ConfigTypeConverter.STR_TO_PAYMENT_TYPE[payment_type]

    # Convert string to log level
    @staticmethod
    def StrToLogLevel(log_level: str) -> int:
        return (ConfigTypeConverter.STR_TO_LOG_LEVEL[log_level]
                if log_level in ConfigTypeConverter.STR_TO_LOG_LEVEL
                else logging.INFO)

    # Convert log level to string
    @staticmethod
    def LogLevelToStr(log_level: int) -> str:
        idx = list(ConfigTypeConverter.STR_TO_LOG_LEVEL.values()).index(log_level)
        return list(ConfigTypeConverter.STR_TO_LOG_LEVEL.keys())[idx]

# Configuration loader base class
class ConfigLoaderBase(ABC):
    # Constructor
    def __init__(self,
                 config: Config,
                 config_parser: configparser.ConfigParser) -> None:
        self.config = config
        self.config_parser = config_parser

    # Load configuration
    @abstractmethod
    def Load(self) -> None:
        pass

    # Print configuration
    @abstractmethod
    def Print(self) -> None:
        pass

    # Set value
    def _SetValue(self,
                  config_type: ConfigTypes,
                  section: str,
                  field: str,
                  fct: Optional[Callable[[str], Any]] = None):
        val = self.config_parser[section][field] if fct is None else fct(self.config_parser[section][field])
        self.config.SetValue(config_type, val)

    # Set value with default
    def _SetValueWithDefault(self,
                             config_type: ConfigTypes,
                             section: str,
                             field: str,
                             default_val: Any,
                             fct: Optional[Callable[[str], Any]] = None):
        try:
            self._SetValue(config_type, section, field, fct)
        except KeyError:
            self.config.SetValue(config_type, default_val)


# Pyrogram config loader
class PyrogramConfigLoader(ConfigLoaderBase):
    # Load configuration
    def Load(self) -> None:
        self._SetValue(ConfigTypes.SESSION_NAME, "pyrogram", "session_name")

    # Print configuration
    def Print(self) -> None:
        print(" - Session name: %s" % self.config.GetValue(ConfigTypes.SESSION_NAME))


# App config loader
class AppConfigLoader(ConfigLoaderBase):
    # Load configuration
    def Load(self) -> None:
        self._SetValue(ConfigTypes.APP_TEST_MODE, "app", "app_test_mode", Utils.StrToBool)
        self._SetValueWithDefault(ConfigTypes.APP_LANG_FILE, "app", "app_lang_file", None)

    # Print configuration
    def Print(self) -> None:
        print(" - App test mode: %s" % self.config.GetValue(ConfigTypes.APP_TEST_MODE))

        lang_file = self.config.GetValue(ConfigTypes.APP_LANG_FILE)
        print(" - App language file: %s" % (lang_file if lang_file is not None else "default"))


# User config loader
class UserConfigLoader(ConfigLoaderBase):
    # Load configuration
    def Load(self) -> None:
        self._SetValue(ConfigTypes.AUTHORIZED_USERS, "users", "authorized_users", lambda val: val.split(","))

    # Print configuration
    def Print(self) -> None:
        print(" - Authorized users: %s" % self.config.GetValue(ConfigTypes.AUTHORIZED_USERS))


# Support config loader
class SupportConfigLoader(ConfigLoaderBase):
    # Load configuration
    def Load(self) -> None:
        self._SetValueWithDefault(ConfigTypes.SUPPORT_EMAIL, "support", "support_email", "")
        self._SetValueWithDefault(ConfigTypes.SUPPORT_TELEGRAM, "support", "support_telegram", "")

    # Print configuration
    def Print(self) -> None:
        print(" - Support email: %s" % self.config.GetValue(ConfigTypes.SUPPORT_EMAIL))
        print(" - Support telegram: %s" % self.config.GetValue(ConfigTypes.SUPPORT_TELEGRAM))


# Payment config loader
class PaymentConfigLoader(ConfigLoaderBase):
    # Default values
    DEF_CREDENTIALS: str = "credentials.json"
    DEF_PICKLE: str = "token.pickle"
    # Maximum column index value
    MAX_COL_IDX: int = 25

    # Load configuration
    def Load(self) -> None:
        self._SetValueWithDefault(ConfigTypes.PAYMENT_WEBSITE, "payment", "payment_website", "")
        self._SetValueWithDefault(ConfigTypes.PAYMENT_CHECK_ON_JOIN, "payment", "payment_check_on_join", True, Utils.StrToBool)
        self._SetValueWithDefault(ConfigTypes.PAYMENT_CHECK_PERIOD_MIN, "payment", "payment_check_period_min", -1, Utils.StrToInt)
        self._SetValueWithDefault(ConfigTypes.PAYMENT_CHECK_CHAT_IDS,
                       "payment",
                       "payment_check_chat_ids",
                       [],
                       lambda val: [Utils.StrToInt(chat_id) for chat_id in val.split(",")] if val != "" else [])

        self._SetValue(ConfigTypes.PAYMENT_TYPE, "payment", "payment_type", ConfigTypeConverter.StrToPaymentType)

        # Load depending on payment type
        payment_type = self.config.GetValue(ConfigTypes.PAYMENT_TYPE)
        if payment_type == PaymentTypes.GOOGLE_SHEET:
            self._SetValue(ConfigTypes.PAYMENT_GOOGLE_SHEET_ID, "payment", "payment_google_sheet_id")
            self._SetValueWithDefault(ConfigTypes.PAYMENT_GOOGLE_CRED, "payment", "payment_google_cred", self.DEF_CREDENTIALS)
            self._SetValueWithDefault(ConfigTypes.PAYMENT_GOOGLE_PICKLE, "payment", "payment_google_pickle", self.DEF_PICKLE)
        elif payment_type == PaymentTypes.EXCEL_FILE:
            self._SetValue(ConfigTypes.PAYMENT_EXCEL_FILE, "payment", "payment_excel_file")

        # Column indexes
        self._SetValueWithDefault(ConfigTypes.PAYMENT_EMAIL_COL, "payment", "payment_email_col", 0, Utils.StrToInt)
        self._SetValueWithDefault(ConfigTypes.PAYMENT_USERNAME_COL, "payment", "payment_username_col", 1, Utils.StrToInt)
        self._SetValueWithDefault(ConfigTypes.PAYMENT_EXPIRATION_COL, "payment", "payment_expiration_col", 2, Utils.StrToInt)
        self._SetValueWithDefault(ConfigTypes.PAYMENT_DATE_FORMAT, "payment", "payment_date_format", "%d/%m/%Y")
        # Check indexes
        self.__CheckColumnIndexes()

    # Print configuration
    def Print(self) -> None:
        print(" - Payment website: %s" % self.config.GetValue(ConfigTypes.PAYMENT_WEBSITE))
        print(" - Payment check on join: %s" % self.config.GetValue(ConfigTypes.PAYMENT_CHECK_ON_JOIN))
        print(" - Payment check period (min): %s" % self.config.GetValue(ConfigTypes.PAYMENT_CHECK_PERIOD_MIN))
        print(" - Payment chat IDs: %s" % self.config.GetValue(ConfigTypes.PAYMENT_CHECK_CHAT_IDS))

        payment_type = self.config.GetValue(ConfigTypes.PAYMENT_TYPE)
        print(" - Payment type: %s" % payment_type)
        if payment_type == PaymentTypes.EXCEL_FILE:
            print(" - Payment Excel file: %s" % self.config.GetValue(ConfigTypes.PAYMENT_EXCEL_FILE))
        elif payment_type == PaymentTypes.GOOGLE_SHEET:
            print(" - Payment Google Sheet ID: %s" % self.config.GetValue(ConfigTypes.PAYMENT_GOOGLE_SHEET_ID))
            print(" - Payment Google credentials file: %s" % self.config.GetValue(ConfigTypes.PAYMENT_GOOGLE_CRED))
            print(" - Payment Google pickle file: %s" % self.config.GetValue(ConfigTypes.PAYMENT_GOOGLE_PICKLE))

        print(" - Payment email column: %s" % self.config.GetValue(ConfigTypes.PAYMENT_EMAIL_COL))
        print(" - Payment username column: %s" % self.config.GetValue(ConfigTypes.PAYMENT_USERNAME_COL))
        print(" - Payment expiration column: %s" % self.config.GetValue(ConfigTypes.PAYMENT_EXPIRATION_COL))
        print(" - Payment date format: %s" % self.config.GetValue(ConfigTypes.PAYMENT_DATE_FORMAT))

    # Check column indexes
    def __CheckColumnIndexes(self):
        email_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EMAIL_COL)
        username_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_USERNAME_COL)
        expiration_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EXPIRATION_COL)

        col_indexes = [email_col_idx, username_col_idx, expiration_col_idx]

        if (email_col_idx == username_col_idx or
                email_col_idx == expiration_col_idx or
                username_col_idx == expiration_col_idx):
            raise ValueError("Invalid payment column indexes, they shall be all different")
        elif any(idx < 0 for idx in col_indexes):
            raise ValueError("Column indexes shall be greater than zero")
        elif any(idx > self.MAX_COL_IDX for idx in col_indexes):
            raise ValueError("Column indexes shall be lower than %d" % self.MAX_COL_IDX)


# Email config loader
class EmailConfigLoader(ConfigLoaderBase):
    # Load configuration
    def Load(self) -> None:
        self._SetValueWithDefault(ConfigTypes.EMAIL_ENABLED, "email", "email_enabled", False, Utils.StrToBool)

        if self.config.GetValue(ConfigTypes.EMAIL_ENABLED):
            self._SetValue(ConfigTypes.EMAIL_FROM, "email", "email_from")
            self._SetValue(ConfigTypes.EMAIL_REPLY_TO, "email", "email_reply_to")
            self._SetValue(ConfigTypes.EMAIL_HOST, "email", "email_host")
            self._SetValue(ConfigTypes.EMAIL_USER, "email", "email_user")
            self._SetValue(ConfigTypes.EMAIL_PASSWORD, "email", "email_password")
            self._SetValue(ConfigTypes.EMAIL_SUBJECT, "email", "email_subject")
            self._SetValue(ConfigTypes.EMAIL_ALT_BODY_FILE, "email", "email_alt_body")
            self._SetValue(ConfigTypes.EMAIL_HTML_BODY_FILE, "email", "email_html_body")
            self.config.SetValue(ConfigTypes.EMAIL_ALT_BODY, self.__ReadFile(ConfigTypes.EMAIL_ALT_BODY_FILE))
            self.config.SetValue(ConfigTypes.EMAIL_HTML_BODY, self.__ReadFile(ConfigTypes.EMAIL_HTML_BODY_FILE))

    # Print configuration
    def Print(self) -> None:
        print(" - Email enabled: %s" % self.config.GetValue(ConfigTypes.EMAIL_ENABLED))

        if self.config.GetValue(ConfigTypes.EMAIL_ENABLED):
            print(" - Email from: %s" % self.config.GetValue(ConfigTypes.EMAIL_FROM))
            print(" - Email reply-to: %s" % self.config.GetValue(ConfigTypes.EMAIL_REPLY_TO))
            print(" - Email host: %s" % self.config.GetValue(ConfigTypes.EMAIL_HOST))
            print(" - Email user: %s" % self.config.GetValue(ConfigTypes.EMAIL_USER))
            print(" - Email password: %s" % self.config.GetValue(ConfigTypes.EMAIL_PASSWORD))
            print(" - Email subject: %s" % self.config.GetValue(ConfigTypes.EMAIL_SUBJECT))
            print(" - Email ALT body file: %s" % self.config.GetValue(ConfigTypes.EMAIL_ALT_BODY_FILE))
            print(" - Email HTML body file: %s" % self.config.GetValue(ConfigTypes.EMAIL_HTML_BODY_FILE))

    # Read file
    def __ReadFile(self,
                   config_type: ConfigTypes) -> str:
        with open(self.config.GetValue(config_type), "r") as fin:
            file_data = fin.read()
        return file_data


# Logging config loader
class LoggingConfigLoader(ConfigLoaderBase):
    # Load configuration
    def Load(self) -> None:
        self._SetValueWithDefault(ConfigTypes.LOG_LEVEL, "logging", "log_level", logging.INFO, ConfigTypeConverter.StrToLogLevel)
        self._SetValueWithDefault(ConfigTypes.LOG_CONSOLE_ENABLED,  "logging", "log_console_enabled", True, Utils.StrToBool)
        self._SetValueWithDefault(ConfigTypes.LOG_FILE_ENABLED,  "logging", "log_file_enabled", False, Utils.StrToBool)

        if self.config.GetValue(ConfigTypes.LOG_FILE_ENABLED):
            self._SetValue(ConfigTypes.LOG_FILE_NAME, "logging", "log_file_name")
            self._SetValue(ConfigTypes.LOG_FILE_APPEND, "logging", "log_file_append", Utils.StrToBool)
            self._SetValue(ConfigTypes.LOG_FILE_MAX_BYTES, "logging", "log_file_max_bytes", Utils.StrToInt)
            self._SetValue(ConfigTypes.LOG_FILE_BACKUP_CNT, "logging", "log_file_backup_cnt", Utils.StrToInt)

    # Print configuration
    def Print(self) -> None:
        print(" - Log level: %s" % ConfigTypeConverter.LogLevelToStr(self.config.GetValue(ConfigTypes.LOG_LEVEL)))
        print(" - Log console enabled: %s" % self.config.GetValue(ConfigTypes.LOG_CONSOLE_ENABLED))
        print(" - Log file enabled: %s" % self.config.GetValue(ConfigTypes.LOG_FILE_ENABLED))

        if self.config.GetValue(ConfigTypes.LOG_FILE_ENABLED):
            print(" - Log file name: %s" % self.config.GetValue(ConfigTypes.LOG_FILE_NAME))
            print(" - Log file append: %s" % self.config.GetValue(ConfigTypes.LOG_FILE_APPEND))
            print(" - Log file max bytes: %s" % self.config.GetValue(ConfigTypes.LOG_FILE_MAX_BYTES))
            print(" - Log file backup count: %s" % self.config.GetValue(ConfigTypes.LOG_FILE_BACKUP_CNT))


# Constant for configuration loader class
class ConfigLoaderConst:
    # Loader classes
    LOADER_CLASSES: List[Type[ConfigLoaderBase]] = [
        PyrogramConfigLoader,
        AppConfigLoader,
        UserConfigLoader,
        SupportConfigLoader,
        PaymentConfigLoader,
        EmailConfigLoader,
        LoggingConfigLoader,
    ]


# Configuration loader class
class ConfigLoader:
    # Constructor
    def __init__(self,
                 config_file: str) -> None:
        self.config_file = config_file
        self.config = Config()

    # Load configuration
    def Load(self) -> None:
        # Read file
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_file)

        # Load configuration
        print("Loaded configuration:")
        for loader_class in ConfigLoaderConst.LOADER_CLASSES:
            loader = loader_class(self.config, config_parser)
            loader.Load()
            loader.Print()
        print("")

    # Get configuration
    def GetConfig(self) -> Config:
        return self.config
