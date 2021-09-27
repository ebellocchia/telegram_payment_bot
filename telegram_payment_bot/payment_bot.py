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
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from telegram_payment_bot.bot_base import BotBase
from telegram_payment_bot.command_dispatcher import CommandTypes
from telegram_payment_bot.payments_checker_task import PaymentsCheckerTask


#
# Classes
#

# Payment bot class
class PaymentBot(BotBase):
    # Constructor
    def __init__(self,
                 config_file: str) -> None:
        super().__init__(config_file)
        # Initialize payment checker
        self.payments_checker_task = PaymentsCheckerTask(self.client,
                                                         self.config,
                                                         self.logger,
                                                         self.translator)

    # Setup handlers
    def _SetupHandlers(self) -> None:
        #
        # Generic
        #

        # Start command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.START_CMD),
            filters.private & filters.command(["start"])))
        # Help command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.HELP_CMD),
            filters.command(["help"])))
        # Alive command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.ALIVE_CMD),
            filters.command(["alive"])))
        # Set test mode command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.SET_TEST_MODE_CMD),
            filters.command(["set_test_mode"])))
        # Check test mode command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.IS_TEST_MODE_CMD),
            filters.command(["is_test_mode"])))
        # Auth_users command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.AUTH_USERS_CMD),
            filters.command(["auth_users"])))
        # Chat info command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.CHAT_INFO_CMD),
            filters.command(["chat_info"])))
        # Users list command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.USERS_LIST_CMD),
            filters.command(["users_list"])))
        # Invite link command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.INVITE_LINKS_CMD),
            filters.command(["invite_link"])))

        #
        # Username
        #

        # Check no username command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.CHECK_NO_USERNAME_CMD),
            filters.command(["check_no_username"])))
        # Remove no username command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.REMOVE_NO_USERNAME_CMD),
            filters.command(["remove_no_username"])))

        #
        # Payments
        #

        # Check payments data command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.SET_CHECK_PAYMENT_ON_JOIN),
            filters.command(["set_check_payment_on_join"])))
        # Check payments data command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.IS_CHECK_PAYMENT_ON_JOIN),
            filters.command(["is_check_payment_on_join"])))
        # Check payments data command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.CHECK_PAYMENTS_DATA_CMD),
            filters.command(["check_payments_data"])))
        # Email no payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.EMAIL_NO_PAYMENT_CMD),
            filters.command(["email_no_payment"])))
        # Check no payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.CHECK_NO_PAYMENT_CMD),
            filters.command(["check_no_payment"])))
        # Remove no payment command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client, message, CommandTypes.REMOVE_NO_PAYMENT_CMD),
            filters.command(["remove_no_payment"])))

        #
        # Payment check task
        #

        # Start payment task command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client,
                                                          message,
                                                          CommandTypes.PAYMENT_TASK_START_CMD,
                                                          payments_checker_task=self.payments_checker_task),
            filters.command(["payment_task_start"])))
        # Stop payment task command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client,
                                                          message,
                                                          CommandTypes.PAYMENT_TASK_STOP_CMD,
                                                          payments_checker_task=self.payments_checker_task),
            filters.command(["payment_task_stop"])))
        # Payment task info command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client,
                                                          message,
                                                          CommandTypes.PAYMENT_TASK_INFO_CMD,
                                                          payments_checker_task=self.payments_checker_task),
            filters.command(["payment_task_info"])))
        # Payment task add chat command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client,
                                                          message,
                                                          CommandTypes.PAYMENT_TASK_ADD_CHAT_CMD,
                                                          payments_checker_task=self.payments_checker_task),
            filters.command(["payment_task_add_chat"])))
        # Payment task remove chat command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client,
                                                          message,
                                                          CommandTypes.PAYMENT_TASK_REMOVE_CHAT_CMD,
                                                          payments_checker_task=self.payments_checker_task),
            filters.command(["payment_task_remove_chat"])))
        # Payment task remove all chats command
        self.client.add_handler(MessageHandler(
            lambda client, message: self._DispatchCommand(client,
                                                          message,
                                                          CommandTypes.PAYMENT_TASK_REMOVE_ALL_CHATS_CMD,
                                                          payments_checker_task=self.payments_checker_task),
            filters.command(["payment_task_remove_all_chats"])))

        # Handler for messages
        self.client.add_handler(MessageHandler(
            lambda client, message: self._HandleMessage(client,
                                                        message,
                                                        payments_checker_task=self.payments_checker_task),
            ~filters.private))
        # Print
        self.logger.GetLogger().info("Bot handlers set")
