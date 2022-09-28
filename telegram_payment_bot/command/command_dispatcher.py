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
from enum import Enum, auto, unique
from typing import Any, Dict, Type

import pyrogram

from telegram_payment_bot.command.command_base import CommandBase
from telegram_payment_bot.command.commands import (
    AliveCmd, AuthUsersCmd, ChatInfoCmd, CheckNoPaymentCmd, CheckNoUsernameCmd, CheckPaymentsDataCmd, EmailNoPaymentCmd,
    HelpCmd, InviteLinkCmd, IsCheckPaymentsOnJoinCmd, IsTestModeCmd, PaymentTaskAddChatCmd, PaymentTaskInfoCmd,
    PaymentTaskRemoveAllChatsCmd, PaymentTaskRemoveChatCmd, PaymentTaskStartCmd, PaymentTaskStopCmd, RemoveNoPaymentCmd,
    RemoveNoUsernameCmd, SetCheckPaymentsOnJoinCmd, SetTestModeCmd, UsersListCmd, VersionCmd
)
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.translator.translation_loader import TranslationLoader


#
# Enumerations
#

# Command types
@unique
class CommandTypes(Enum):
    # Generic
    START_CMD = auto()
    HELP_CMD = auto()
    ALIVE_CMD = auto()
    SET_TEST_MODE_CMD = auto()
    IS_TEST_MODE_CMD = auto()
    AUTH_USERS_CMD = auto()
    CHAT_INFO_CMD = auto()
    USERS_LIST_CMD = auto()
    INVITE_LINKS_CMD = auto()
    VERSION_CMD = auto()
    # Username
    CHECK_NO_USERNAME_CMD = auto()
    REMOVE_NO_USERNAME_CMD = auto()
    # Payment
    SET_CHECK_PAYMENT_ON_JOIN = auto()
    IS_CHECK_PAYMENT_ON_JOIN = auto()
    CHECK_PAYMENTS_DATA_CMD = auto()
    EMAIL_NO_PAYMENT_CMD = auto()
    CHECK_NO_PAYMENT_CMD = auto()
    REMOVE_NO_PAYMENT_CMD = auto()
    # Payment check task
    PAYMENT_TASK_START_CMD = auto()
    PAYMENT_TASK_STOP_CMD = auto()
    PAYMENT_TASK_ADD_CHAT_CMD = auto()
    PAYMENT_TASK_REMOVE_CHAT_CMD = auto()
    PAYMENT_TASK_REMOVE_ALL_CHATS_CMD = auto()
    PAYMENT_TASK_INFO_CMD = auto()


#
# Classes
#

# Comstant for command dispatcher class
class CommandDispatcherConst:
    # Command to class map
    CMD_TYPE_TO_CLASS: Dict[CommandTypes, Type[CommandBase]] = {
        # Generic
        CommandTypes.START_CMD: HelpCmd,
        CommandTypes.HELP_CMD: HelpCmd,
        CommandTypes.ALIVE_CMD: AliveCmd,
        CommandTypes.SET_TEST_MODE_CMD: SetTestModeCmd,
        CommandTypes.IS_TEST_MODE_CMD: IsTestModeCmd,
        CommandTypes.AUTH_USERS_CMD: AuthUsersCmd,
        CommandTypes.CHAT_INFO_CMD: ChatInfoCmd,
        CommandTypes.USERS_LIST_CMD: UsersListCmd,
        CommandTypes.INVITE_LINKS_CMD: InviteLinkCmd,
        CommandTypes.VERSION_CMD: VersionCmd,
        # Username
        CommandTypes.CHECK_NO_USERNAME_CMD: CheckNoUsernameCmd,
        CommandTypes.REMOVE_NO_USERNAME_CMD: RemoveNoUsernameCmd,
        # Payment
        CommandTypes.SET_CHECK_PAYMENT_ON_JOIN: SetCheckPaymentsOnJoinCmd,
        CommandTypes.IS_CHECK_PAYMENT_ON_JOIN: IsCheckPaymentsOnJoinCmd,
        CommandTypes.CHECK_PAYMENTS_DATA_CMD: CheckPaymentsDataCmd,
        CommandTypes.EMAIL_NO_PAYMENT_CMD: EmailNoPaymentCmd,
        CommandTypes.CHECK_NO_PAYMENT_CMD: CheckNoPaymentCmd,
        CommandTypes.REMOVE_NO_PAYMENT_CMD: RemoveNoPaymentCmd,
        # Payment check task
        CommandTypes.PAYMENT_TASK_START_CMD: PaymentTaskStartCmd,
        CommandTypes.PAYMENT_TASK_STOP_CMD: PaymentTaskStopCmd,
        CommandTypes.PAYMENT_TASK_INFO_CMD: PaymentTaskInfoCmd,
        CommandTypes.PAYMENT_TASK_ADD_CHAT_CMD: PaymentTaskAddChatCmd,
        CommandTypes.PAYMENT_TASK_REMOVE_CHAT_CMD: PaymentTaskRemoveChatCmd,
        CommandTypes.PAYMENT_TASK_REMOVE_ALL_CHATS_CMD: PaymentTaskRemoveAllChatsCmd,
    }


# Command dispatcher class
class CommandDispatcher:

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader

    # Constructor
    def __init__(self,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.translator = translator

    # Dispatch command
    def Dispatch(self,
                 client: pyrogram.Client,
                 message: pyrogram.types.Message,
                 cmd_type: CommandTypes,
                 **kwargs: Any) -> None:
        if not isinstance(cmd_type, CommandTypes):
            raise TypeError("Command type is not an enumerative of CommandTypes")

        # Log
        self.logger.GetLogger().info(f"Dispatching command type: {cmd_type}")

        # Create and execute command if existent
        if cmd_type in CommandDispatcherConst.CMD_TYPE_TO_CLASS:
            cmd_class = CommandDispatcherConst.CMD_TYPE_TO_CLASS[cmd_type](client,
                                                                           self.config,
                                                                           self.logger,
                                                                           self.translator)
            cmd_class.Execute(message, **kwargs)
