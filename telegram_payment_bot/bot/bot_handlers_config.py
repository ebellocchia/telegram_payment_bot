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

from pyrogram import filters
from pyrogram.handlers import MessageHandler

from telegram_payment_bot.bot.bot_handlers_config_typing import BotHandlersConfigType
from telegram_payment_bot.command.command_dispatcher import CommandTypes
from telegram_payment_bot.message.message_dispatcher import MessageTypes


BotHandlersConfig: BotHandlersConfigType = {
    MessageHandler: [
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.START_CMD),
            "filters": filters.private & filters.command(["start"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.HELP_CMD),
            "filters": filters.command(["help"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.ALIVE_CMD),
            "filters": filters.command(["alive"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.SET_TEST_MODE_CMD),
            "filters": filters.command(["paybot_set_test_mode"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.IS_TEST_MODE_CMD),
            "filters": filters.command(["paybot_is_test_mode"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.AUTH_USERS_CMD),
            "filters": filters.command(["paybot_auth_users"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.CHAT_INFO_CMD),
            "filters": filters.command(["paybot_chat_info"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.USERS_LIST_CMD),
            "filters": filters.command(["paybot_users_list"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.INVITE_LINKS_CMD),
            "filters": filters.command(["paybot_invite_link"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.VERSION_CMD),
            "filters": filters.command(["paybot_version"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.CHECK_NO_USERNAME_CMD),
            "filters": filters.command(["paybot_check_username"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.REMOVE_NO_USERNAME_CMD),
            "filters": filters.command(["paybot_remove_username"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.SET_CHECK_PAYMENT_ON_JOIN),
            "filters": filters.command(["paybot_set_check_on_join"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.IS_CHECK_PAYMENT_ON_JOIN),
            "filters": filters.command(["paybot_is_check_on_join"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.CHECK_PAYMENTS_DATA_CMD),
            "filters": filters.command(["paybot_check_data"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.EMAIL_NO_PAYMENT_CMD),
            "filters": filters.command(["paybot_email_payment"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.CHECK_NO_PAYMENT_CMD),
            "filters": filters.command(["paybot_check_payment"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client, message, CommandTypes.REMOVE_NO_PAYMENT_CMD),
            "filters": filters.command(["paybot_remove_payment"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(
                client, message, CommandTypes.PAYMENT_TASK_START_CMD, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.command(["paybot_task_start"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(
                client, message, CommandTypes.PAYMENT_TASK_STOP_CMD, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.command(["paybot_task_stop"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(
                client, message, CommandTypes.PAYMENT_TASK_ADD_CHAT_CMD, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.command(["paybot_task_add_chat"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(
                client, message, CommandTypes.PAYMENT_TASK_REMOVE_CHAT_CMD, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.command(["paybot_task_remove_chat"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(
                client, message, CommandTypes.PAYMENT_TASK_REMOVE_ALL_CHATS_CMD, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.command(["paybot_task_remove_all_chats"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(
                client, message, CommandTypes.PAYMENT_TASK_INFO_CMD, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.command(["paybot_task_info"]),
        },
        {
            "callback": lambda self, client, message: self.HandleMessage(client, message, MessageTypes.GROUP_CHAT_CREATED),
            "filters": filters.group_chat_created,
        },
        {
            "callback": lambda self, client, message: self.HandleMessage(client, message, MessageTypes.NEW_CHAT_MEMBERS),
            "filters": filters.new_chat_members,
        },
        {
            "callback": lambda self, client, message: self.HandleMessage(
                client, message, MessageTypes.LEFT_CHAT_MEMBER, payments_check_scheduler=self.payments_check_scheduler
            ),
            "filters": filters.left_chat_member,
        },
    ],
}
