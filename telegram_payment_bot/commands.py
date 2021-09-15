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
from typing import Any, Callable
from telegram_payment_bot.chat_members import ChatMembersGetter
from telegram_payment_bot.command_base import CommandBase
from telegram_payment_bot.command_data import CommandParameterError
from telegram_payment_bot.config import ConfigTypes
from telegram_payment_bot.members_kicker import MembersKicker
from telegram_payment_bot.payments_checker import PaymentsChecker
from telegram_payment_bot.special_users_list import AuthorizedUsersList
from telegram_payment_bot.helpers import ChatHelper, UserHelper
from telegram_payment_bot.payments_data import PaymentErrorTypes
from telegram_payment_bot.payments_emailer import PaymentsEmailer
from telegram_payment_bot.payments_loader_factory import PaymentsLoaderFactory
from telegram_payment_bot.username_checker import UsernameChecker


#
# Decorators
#

# Decorator for group-only commands
def GroupChatOnly(exec_cmd_fct: Callable[[Any], None]) -> Callable[[Any], None]:
    def decorated(self):
        # Check if private chat
        if self._IsPrivateChat():
            self._SendMessage(self.translator.GetSentence("GROUP_ONLY_ERR"))
        else:
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
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("HELP_CMD") % UserHelper.GetName(self.cmd_data.User()))


#
# Command for checking if bot is alive
#
class AliveCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("ALIVE_CMD"))


#
# Command for setting test mode
#
class SetTestModeCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        try:
            # Get parameters
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_PARAM_ERR_CMD"))
        else:
            # Set test mode
            self.config.SetValue(ConfigTypes.APP_TEST_MODE, flag)

            # Send message
            if self.config.GetValue(ConfigTypes.APP_TEST_MODE):
                self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_EN_CMD"))
            else:
                self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_DIS_CMD"))


#
# Command for checking if test mode
#
class IsTestModeCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        if self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_EN_CMD"))
        else:
            self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_DIS_CMD"))


#
# Command for getting authorized users
#
class AuthUsersCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("AUTH_USERS_CMD") % AuthorizedUsersList(self.config).ToString())


#
# Command for getting chat information
#
class ChatInfoCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("CHAT_INFO_CMD") %
                          (ChatHelper.GetTitle(self.cmd_data.Chat()),
                          self.cmd_data.Chat().type,
                          self.cmd_data.Chat().id))


#
# Command for getting the users list
#
class UsersListCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get chat members
        chat_members = ChatMembersGetter(self.client, self.config).GetAll(self.cmd_data.Chat())
        # Send message
        self._SendMessage(self.translator.GetSentence("USERS_LIST_CMD") %
                          (ChatHelper.GetTitle(self.cmd_data.Chat()), chat_members.ToString()))


#
# Command for generating a new invite link
#
class InviteLinkCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._NewInviteLink()


#
# Command for checking users with no username
#
class CheckNoUsernameCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get chat members
        chat_members = UsernameChecker(self.client, self.config).GetAllWithNoUsername(self.cmd_data.Chat())

        # Build message
        if chat_members.Any():
            # Get parameter
            left_hours = self.cmd_data.Params().GetAsInt(0, 0)

            msg = (self.translator.GetSentence("CHECK_NO_USERNAME_P1_CMD") %
                   (ChatHelper.GetTitle(self.cmd_data.Chat()),
                    chat_members.Count(),
                    chat_members.ToString(),
                    self.__HoursToStr(left_hours)))

            # Add contact information if any
            support_email = self.config.GetValue(ConfigTypes.SUPPORT_EMAIL)
            support_tg = self.config.GetValue(ConfigTypes.SUPPORT_TELEGRAM)
            if support_email != "" and support_tg != "":
                msg += self.translator.GetSentence("CHECK_NO_USERNAME_P2_CMD") % (support_email, support_tg)
            elif support_email != "":
                msg += self.translator.GetSentence("CHECK_NO_USERNAME_P3_CMD") % support_email
            elif support_tg != "":
                msg += self.translator.GetSentence("CHECK_NO_USERNAME_P4_CMD") % support_tg
        else:
            msg = self.translator.GetSentence("CHECK_NO_USERNAME_P5_CMD") % ChatHelper.GetTitle(self.cmd_data.Chat())

        # Send message
        self._SendMessage(msg)

    # Get time string
    def __HoursToStr(self,
                     hours: int) -> str:
        if hours > 47:
            return self.translator.GetSentence("WITHIN_DAYS_MSG") % (hours // 24)
        elif hours > 1:
            return self.translator.GetSentence("WITHIN_HOURS_MSG") % hours
        else:
            return self.translator.GetSentence("ASAP_MSG")


#
# Command for removing users with no username
#
class RemoveNoUsernameCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Notice before removing
        self._SendMessage(self.translator.GetSentence("REMOVE_NO_USERNAME_P1_CMD") %
                          ChatHelper.GetTitle(self.cmd_data.Chat()))

        # Kick members if any
        kicked_members = MembersKicker(self.client,
                                       self.config,
                                       self.logger).KickAllWithNoUsername(self.cmd_data.Chat())

        # Build message
        msg = self.translator.GetSentence("REMOVE_NO_USERNAME_P2_CMD") % kicked_members.Count()
        if kicked_members.Any():
            msg += self.translator.GetSentence("REMOVE_NO_USERNAME_P3_CMD") % kicked_members.ToString()

        # Send message
        self._SendMessage(msg)
        # Generate new invite link if necessary
        if kicked_members.Any():
            self._NewInviteLink()


#
# Command for checking payments data for errors
#
class CheckPaymentsDataCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("CHECK_PAYMENTS_DATA_P1_CMD"))

        # Check payments data
        payments_loader = PaymentsLoaderFactory(self.config, self.logger).CreateLoader()
        payments_data_err = payments_loader.CheckForErrors()

        # Check results
        if payments_data_err.Any():
            msg = self.translator.GetSentence("CHECK_PAYMENTS_DATA_P2_CMD") % payments_data_err.Count()

            for payment_err in payments_data_err:
                if payment_err.Type() == PaymentErrorTypes.DUPLICATED_USERNAME_ERR:
                    msg += self.translator.GetSentence("CHECK_PAYMENTS_DATA_P3_CMD") % (
                        payment_err.Username(), payment_err.Row())
                elif payment_err.Type() == PaymentErrorTypes.INVALID_DATE_ERR:
                    msg += self.translator.GetSentence("CHECK_PAYMENTS_DATA_P4_CMD") % (
                        payment_err.Username(), payment_err.Row(), payment_err.ExpirationDate())
        else:
            msg = self.translator.GetSentence("CHECK_PAYMENTS_DATA_P5_CMD")

        # Send message
        self._SendMessage(msg)


#
# Command for sending email to users with no payment
#
class EmailNoPaymentCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        if not self.config.GetValue(ConfigTypes.EMAIL_ENABLED):
            msg = self.translator.GetSentence("EMAIL_NO_PAYMENT_DISABLED_CMD")
        else:
            # Get parameter
            days_left = self.cmd_data.Params().GetAsInt(0, 0)
            # Get expired payments
            expired_payments = PaymentsEmailer(self.client,
                                               self.config,
                                               self.logger).EmailAllWithExpiringPayment(days_left)

            # Build message
            if expired_payments.Any():
                # Build strings for easier reading
                days_left_str = (self.translator.GetSentence("IN_DAYS_MSG") % days_left
                                 if days_left > 1 else
                                 (self.translator.GetSentence("TOMORROW_MSG")
                                  if days_left == 1 else
                                  self.translator.GetSentence("TODAY_MSG")))

                msg = (self.translator.GetSentence("EMAIL_NO_PAYMENT_P1_CMD") %
                       (days_left_str, expired_payments.Count(), expired_payments.ToString()))
            else:
                msg = self.translator.GetSentence("EMAIL_NO_PAYMENT_P2_CMD")

        # Send message
        self._SendMessage(msg)


#
# Command for checking users with no payment
#
class CheckNoPaymentCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        days_left = self.cmd_data.Params().GetAsInt(0, 0)
        last_day = self.cmd_data.Params().GetAsInt(1, 0)
        # Get expired members
        expired_members = PaymentsChecker(self.client,
                                          self.config,
                                          self.logger).GetAllMembersWithExpiringPayment(self.cmd_data.Chat(), days_left)

        # Build message
        if expired_members.Any():
            # Build strings for easier reading
            days_left_str = (self.translator.GetSentence("IN_DAYS_MSG") % days_left
                             if days_left > 1 else
                             (self.translator.GetSentence("TOMORROW_MSG")
                              if days_left == 1 else
                              self.translator.GetSentence("TODAY_MSG")))
            last_day_str = (self.translator.GetSentence("DAY_OF_MONTH_MSG") % last_day
                            if 1 <= last_day <= 31
                            else self.translator.GetSentence("FEW_DAYS_MSG"))

            # Build message
            msg = (self.translator.GetSentence("CHECK_NO_PAYMENT_P1_CMD") %
                   (ChatHelper.GetTitle(self.cmd_data.Chat()),
                    days_left_str,
                    expired_members.Count(),
                    expired_members.ToString(),
                    last_day_str))

            # Add website if any
            website = self.config.GetValue(ConfigTypes.PAYMENT_WEBSITE)
            if website != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_P2_CMD") % website

            # Add contact information if any
            support_email = self.config.GetValue(ConfigTypes.SUPPORT_EMAIL)
            support_tg = self.config.GetValue(ConfigTypes.SUPPORT_TELEGRAM)
            if support_email != "" and support_tg != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_P3_CMD") % (support_email, support_tg)
            elif support_email != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_P4_CMD") % support_email
            elif support_tg != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_P5_CMD") % support_tg
        else:
            msg = self.translator.GetSentence("CHECK_NO_PAYMENT_P6_CMD") % ChatHelper.GetTitle(self.cmd_data.Chat())

        # Send message
        self._SendMessage(msg)


#
# Command for removing users with no payment
#
class RemoveNoPaymentCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Notice before removing
        self._SendMessage(self.translator.GetSentence("REMOVE_NO_PAYMENT_P1_CMD") %
                          ChatHelper.GetTitle(self.cmd_data.Chat()))

        # Kick members if any
        kicked_members = MembersKicker(self.client,
                                       self.config,
                                       self.logger).KickAllWithExpiredPayment(self.cmd_data.Chat())

        # Build message
        msg = self.translator.GetSentence("REMOVE_NO_PAYMENT_P2_CMD") % kicked_members.Count()
        if kicked_members.Any():
            msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_P3_CMD") % kicked_members.ToString()

        # Send message
        self._SendMessage(msg)
        # Generate new invite link if necessary
        if kicked_members.Any():
            self._NewInviteLink()
