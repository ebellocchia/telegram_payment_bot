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
import pyrogram
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from telegram_payment_bot.command_dispatcher import CommandDispatcher, CommandTypes
from telegram_payment_bot.config import ConfigTypes
from telegram_payment_bot.config_loader import ConfigLoader
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.message_dispatcher import MessageDispatcher
from telegram_payment_bot.payments_periodic_checker import PaymentsPeriodicChecker
from telegram_payment_bot.translation_loader import TranslationLoader


#
# Classes
#

# Payment bot class
class PaymentBot:
    # Constructor
    def __init__(self) -> None:
        self.config = None
        self.logger = None
        self.client = None
        self.payments_periodic_checker = None

    # Initialize
    def Init(self,
             config_file: str) -> None:
        # Load configuration
        self.__LoadConfiguration(config_file)
        # Initialize logger and translations
        self.__InitLogging()
        self.__InitTranslations()
        # Initialize client
        self.__InitClient(config_file)
        # Initialize payment checker
        self.__InitPaymentChecker()
        # Setup handlers
        self.__SetupHandlers()
        # Log
        self.logger.GetLogger().info("Bot initialization completed")

    # Run bot
    def Run(self) -> None:
        # Print
        self.logger.GetLogger().info("Payment Telegram Bot started!\n")
        # Run periodic checker
        self.payments_periodic_checker.Start()
        # Run client
        self.client.run()

    # Load configuration
    def __LoadConfiguration(self,
                            config_file: str) -> None:
        config_ldr = ConfigLoader(config_file)
        config_ldr.Load()
        self.config = config_ldr.GetConfig()

    # Initialize logging
    def __InitLogging(self) -> None:
        self.logger = Logger(self.config)
        self.logger.Init()

    # Initialize translation
    def __InitTranslations(self) -> None:
        self.translator = TranslationLoader(self.logger)
        self.translator.Load(self.config.GetValue(ConfigTypes.APP_LANG_FILE))

    # Initialize client
    def __InitClient(self,
                     config_file: str) -> None:
        self.client = Client(self.config.GetValue(ConfigTypes.SESSION_NAME), config_file=config_file)

    # Initialize payment checker
    def __InitPaymentChecker(self) -> None:
        self.payments_periodic_checker = PaymentsPeriodicChecker(self.client,
                                                                 self.config,
                                                                 self.logger,
                                                                 self.translator)
        self.payments_periodic_checker.Init()

    # Setup handlers
    def __SetupHandlers(self) -> None:
        # Start command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.START_CMD),
            filters.private & filters.command(["start"])))
        # Help command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.HELP_CMD),
            filters.command(["help"])))
        # Alive command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.ALIVE_CMD),
            filters.command(["alive"])))
        # Set test mode command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.SET_TEST_MODE_CMD),
            filters.command(["set_test_mode"])))
        # Check test mode command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.IS_TEST_MODE_CMD),
            filters.command(["is_test_mode"])))
        # Auth_users command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.AUTH_USERS_CMD),
            filters.command(["auth_users"])))
        # Chat info command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.CHAT_INFO_CMD),
            filters.command(["chat_info"])))
        # Users_list command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.USERS_LIST_CMD),
            filters.command(["users_list"])))
        # Invite_link command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.INVITE_LINKS_CMD),
            filters.command(["invite_link"])))
        # Check_no_username command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.CHECK_NO_USERNAME_CMD),
            filters.command(["check_no_username"])))
        # Remove_no_username command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.REMOVE_NO_USERNAME_CMD),
            filters.command(["remove_no_username"])))
        # Email_no_payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.CHECK_PAYMENTS_DATA_CMD),
            filters.command(["check_payments_data"])))
        # Email_no_payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.EMAIL_NO_PAYMENT_CMD),
            filters.command(["email_no_payment"])))
        # Check_no_payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.CHECK_NO_PAYMENT_CMD),
            filters.command(["check_no_payment"])))
        # Remove_no_payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.REMOVE_NO_PAYMENT_CMD),
            filters.command(["remove_no_payment"])))
        # Handler for messages
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__HandleMessage(client, message),
            ~filters.private))
        # Print
        self.logger.GetLogger().info("Bot handlers set")

    # Dispatch command
    def __DispatchCommand(self,
                          client: pyrogram.Client,
                          message: pyrogram.types.Message,
                          cmd_type: CommandTypes) -> None:
        cmd_dispatcher = CommandDispatcher(self.config, self.logger, self.translator)
        cmd_dispatcher.Dispatch(client, message, cmd_type)

    # Handle message
    def __HandleMessage(self,
                        client: pyrogram.Client,
                        message: pyrogram.types.Message) -> None:
        msg_dispatcher = MessageDispatcher(self.config, self.logger, self.translator)
        msg_dispatcher.Dispatch(client, message)
