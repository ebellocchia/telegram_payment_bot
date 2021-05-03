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
from typing import Callable, Type
from telegram_payment_bot.chat_members import ChatMembersGetter
from telegram_payment_bot.command_base import CommandBase
from telegram_payment_bot.config import ConfigTypes
from telegram_payment_bot.members_kicker import MembersKicker
from telegram_payment_bot.payments_checker import PaymentsChecker
from telegram_payment_bot.special_users_list import AuthorizedUsersList
from telegram_payment_bot.user_helper import UserHelper
from telegram_payment_bot.payments_emailer import PaymentsEmailer
from telegram_payment_bot.username_checker import UsernameChecker


#
# Decorators
#

# Decorator for group-only commands
def GroupChatOnly(exec_cmd_fct: Callable[[Type[CommandBase]], None]) -> Callable[[Type[CommandBase]], None]:
    def decorated(self):
        # Check if private chat
        if self._IsChatPrivate():
            self._SendMessage("**ERROR**\nThis command can be executed only in the chat group.")
            return
        exec_cmd_fct(self)

    return decorated


#
# Classes
#

#
# Command for getting help
#
class HelpCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self) -> None:
        # Build message
        msg = "**HELP**\n"
        msg += "Hi %s,\n" % UserHelper.GetName(self.cmd_data.User())
        msg += "welcome to the Payment Telegram Bot.\n"
        msg += "Here is the list of supported commands.\n"
        msg += "\n**Generic**\n"
        msg += "/help : show this message\n"
        msg += "/alive : show if bot is active\n"
        msg += "/auth_users : show the list of users authorized to use the bot\n"
        msg += "/chat_info : show the chat information - **Only group**\n"
        msg += "/users_list : show the list of all users in group - **Only group**\n"
        msg += "/invite_link : generate a new invite link - **Only group**\n"
        msg += "\n**Username Check**\n"
        msg += "/check_no_username [HOURS_LEFT] : show users with no username - **Only group**\n"
        msg += "/remove_no_username : remove users with no username - **Only group**\n"
        msg += "\n**Payments Check**\n"
        msg += "/email_no_payment [DAYS_LEFT]: send a reminder email to users whose payments is about to expire\n"
        msg += "/check_no_payment [DAYS_LEFT] [LAST_DAY]: show users whose payments is about to expire - **Only group**\n"
        msg += "/remove_no_payment : remove users whose payment is expired - **Only group**\n"
        msg += "\nCommands that can be executed only in chat group are specified in bold text.\n"
        msg += "\n**NOTE:** it's possible to add \"quiet\" o \"q\" as last parameter to get the result in a private chat, to avoid flooding the chat group."

        # Send message
        self._SendMessage(msg)


#
# Command for checking if bot is alive
#
class AliveCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self) -> None:
        self._SendMessage("**STATUS**\nThe bot is alive.")


#
# Command for getting authorized users
#
class AuthUsersCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self) -> None:
        # Build message
        msg = "**AUTHORIZED USERS**\n"
        msg += "Users authorized to use the bot:\n%s\n" % AuthorizedUsersList(self.config).ToString()
        # Send message
        self._SendMessage(msg)


#
# Command for getting chat information
#
class ChatInfoCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        # Build message
        msg = "**CHAT INFORMATION**\n"
        msg += "Name: %s\n" % (self.cmd_data.Chat().title if self.cmd_data.Chat().title is not None else "not specified")
        msg += "Type: %s\n" % self.cmd_data.Chat().type
        msg += "ID: %d" % self.cmd_data.Chat().id
        # Send message
        self._SendMessage(msg)


#
# Command for getting the users list
#
class UsersListCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        # Get chat members
        chat_members = ChatMembersGetter(self.client, self.config).GetAll(self.cmd_data.Chat())
        # Build message
        msg = "**USERS LIST**\n"
        msg += "Chat group: **%s**\n" % self.cmd_data.Chat().title
        msg += "Users list:\n%s" % chat_members.ToString()
        # Send message
        self._SendMessage(msg)


#
# Command for generating a new invite link
#
class InviteLinkCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        self._NewInviteLink()


#
# Command for checking users with no username
#
class CheckNoUsernameCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        # Get chat members
        chat_members = UsernameChecker(self.client, self.config).GetAllWithNoUsername(self.cmd_data.Chat())

        # Build message
        if chat_members.Any():
            # Get parameter
            left_hours = self.cmd_data.Params().GetAsInt(0)

            msg = "**USERNAME CHECK**\n"
            msg += "Chat group: **%s**\n" % self.cmd_data.Chat().title
            msg += "Members with no username: **%d**\n" % chat_members.Count()
            msg += "Members list:\n%s\n" % chat_members.ToString()
            msg += "Please set the username %s or you'll be removed from the group.\n" % self.__HoursToStr(left_hours)
            msg += "To set it: **Settings -> Edit Profile -> username**.\n\n"

            support_email =  self.config.GetValue(ConfigTypes.SUPPORT_EMAIL)
            if support_email != "":
                msg += "**The username shall be sent via email to: ** %s." % support_email
        else:
            msg = "**USERNAME CHECK**\nChat group: **%s**\nAll members has the username set." % self.cmd_data.Chat().title

        # Send message
        self._SendMessage(msg)

    # Get time string
    @staticmethod
    def __HoursToStr(hours: int) -> str:
        if hours > 47:
            return "within %d days" % (hours // 24)
        elif hours > 1:
            return "within %d hours" % hours
        else:
            return "as soon as possible"


#
# Command for removing users with no username
#
class RemoveNoUsernameCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        # Notice before removing
        self._SendMessage(
            "**USERNAME CHECK**\nChat group: **%s**\nThe members without username are going to be removed." % self.cmd_data.Chat().title)

        # Kick members if any
        kicked_members = MembersKicker(self.client, self.config, self.logger).KickAllWithNoUsername(self.cmd_data.Chat())

        # Build message
        msg = "Operation completed. Removed members: **%d**" % kicked_members.Count()
        if kicked_members.Any():
            msg += "\nMembers list:\n%s" % kicked_members.ToString()

        # Send message
        self._SendMessage(msg)
        # Generate new invite link if necessary
        if kicked_members.Any():
            self._NewInviteLink()


#
# Command for sending email to users with no payment
#
class EmailNoPaymentCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self) -> None:
        if not self.config.GetValue(ConfigTypes.EMAIL_ENABLED):
            msg = "**PAYMENTS CHECK**\nEmail is currently disabled."
        else:
            # Get parameter
            days_left = self.cmd_data.Params().GetAsInt(0)
            # Get expired payments
            expired_payments = PaymentsEmailer(self.client, self.config, self.logger).EmailAllWithExpiringPayment(days_left)

            # Build message
            if expired_payments.Any():
                # Build strings for easier reading
                days_left_str = "in %d days" % days_left if days_left > 1 else ("tomorrow" if days_left == 1 else "today")

                msg = "**PAYMENTS CHECK**\n"
                msg += "Members whose payment is about to expire %s: **%d**\n" % (days_left_str, expired_payments.Count())
                msg += "Members list:\n%s\n" % expired_payments.ToString()
                msg += "A reminder email has been sent to all members."
            else:
                msg = "**PAYMENTS CHECK**\nAll members paid, no email sent."

        # Send message
        self._SendMessage(msg)


#
# Command for checking users with no payment
#
class CheckNoPaymentCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        # Get parameters
        days_left = self.cmd_data.Params().GetAsInt(0)
        last_day = self.cmd_data.Params().GetAsInt(1)
        # Get expired members
        expired_members = PaymentsChecker(self.client, self.config, self.logger).GetAllMembersWithExpiringPayment(self.cmd_data.Chat(), days_left)

        # Build message
        if expired_members.Any():
            # Build strings for easier reading
            days_left_str = "in %d days" % days_left if days_left > 1 else ("tomorrow" if days_left == 1 else "today")
            last_day_str = "day %d of the month" % last_day if 1 <= last_day <= 31 else "few days"

            msg = "**PAYMENTS CHECK**\n"
            msg += "Chat group: **%s**\n" % self.cmd_data.Chat().title
            msg += "Members whose payment is about to expire %s: **%d**\n" % (days_left_str, expired_members.Count())
            msg += "Members list:\n%s\n" % expired_members.ToString()
            msg += "Please pay within %s or you'll be removed from the group.\n" % last_day_str

            website = self.config.GetValue(ConfigTypes.PAYMENT_WEBSITE)
            if website != "":
                msg += "You can pay directly on the website: %s\n\n" % website

            support_email =  self.config.GetValue(ConfigTypes.SUPPORT_EMAIL)
            support_tg = self.config.GetValue(ConfigTypes.SUPPORT_TELEGRAM)

            if support_email != "" and support_tg != "":
                msg += "If you are on the list but you paid, please send an email to %s or contact @%s **specifying your Telegram username**." % (
                    support_email, support_tg)
            elif support_email != "":
                msg += "If you are on the list but you paid, please send an email to %s **specifying your Telegram username**." % support_email
            elif support_tg != "":
                msg += "If you are on the list but you paid, please contact @%s **specifying your Telegram username**." % support_tg
        else:
            msg = "**PAYMENTS CHECK**\nChat group: **%s**\nAll members paid." % self.cmd_data.Chat().title

        # Send message
        self._SendMessage(msg)


#
# Command for removing users with no payment
#
class RemoveNoPaymentCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self) -> None:
        # Notice before removing
        self._SendMessage("**PAYMENTS CHECK**\nChat group: **%s**\nMembers whose payment is about to expire are going to be removed." % self.cmd_data.Chat().title)

        # Kick members if any
        kicked_members = MembersKicker(self.client, self.config, self.logger).KickAllWithExpiredPayment(self.cmd_data.Chat())

        # Build message
        msg = "Operation completed. Removed members: **%d**" % kicked_members.Count()
        if kicked_members.Any():
            msg += "\nMembers list:\n%s" % kicked_members.ToString()

        # Send message
        self._SendMessage(msg)
        # Generate new invite link if necessary
        if kicked_members.Any():
            self._NewInviteLink()
