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

from typing import Any, Callable

from telegram_payment_bot._version import __version__
from telegram_payment_bot.auth_user.authorized_users_list import AuthorizedUsersList
from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.command.command_base import CommandBase
from telegram_payment_bot.command.command_data import CommandParameterError
from telegram_payment_bot.email.smtp_emailer import SmtpEmailerError
from telegram_payment_bot.member.members_kicker import MembersKicker
from telegram_payment_bot.member.members_payment_getter import MembersPaymentGetter
from telegram_payment_bot.member.members_username_getter import MembersUsernameGetter
from telegram_payment_bot.misc.chat_members import ChatMembersGetter, ChatMembersList
from telegram_payment_bot.misc.helpers import ChatHelper, UserHelper
from telegram_payment_bot.payment.payments_check_scheduler import (
    PaymentsCheckJobAlreadyRunningError,
    PaymentsCheckJobChatAlreadyPresentError,
    PaymentsCheckJobChatNotPresentError,
    PaymentsCheckJobInvalidPeriodError,
    PaymentsCheckJobNotRunningError,
)
from telegram_payment_bot.payment.payments_data import PaymentErrorTypes
from telegram_payment_bot.payment.payments_emailer import PaymentsEmailer
from telegram_payment_bot.payment.payments_loader_factory import PaymentsLoaderFactory


def GroupChatOnly(exec_cmd_fct: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for group-only commands.

    Args:
        exec_cmd_fct: Command execution function

    Returns:
        Decorated function that checks for group chat
    """

    async def decorated(self,
                        **kwargs: Any):
        if self._IsPrivateChat():
            await self._SendMessage(self.translator.GetSentence("GROUP_ONLY_ERR_MSG"))
        else:
            await exec_cmd_fct(self, **kwargs)

    return decorated


class HelpCmd(CommandBase):
    """Command for getting help."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the help command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(self.translator.GetSentence("HELP_CMD",
                                                            name=UserHelper.GetName(self.cmd_data.User())))


class AliveCmd(CommandBase):
    """Command for checking if bot is alive."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the alive command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(self.translator.GetSentence("ALIVE_CMD"))


class SetTestModeCmd(CommandBase):
    """Command for setting test mode."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the set test mode command.

        Args:
            **kwargs: Additional keyword arguments
        """
        try:
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            self.config.SetValue(BotConfigTypes.APP_TEST_MODE, flag)

            if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
                await self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_EN_CMD"))
            else:
                await self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_DIS_CMD"))


class IsTestModeCmd(CommandBase):
    """Command for checking if test mode is enabled."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the is test mode command.

        Args:
            **kwargs: Additional keyword arguments
        """
        if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            await self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_EN_CMD"))
        else:
            await self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_DIS_CMD"))


class AuthUsersCmd(CommandBase):
    """Command for getting authorized users."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the authorized users command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(self.translator.GetSentence("AUTH_USERS_CMD", auth_users_list=str(AuthorizedUsersList(self.config))))


class ChatInfoCmd(CommandBase):
    """Command for getting chat information."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the chat info command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(
            self.translator.GetSentence(
                "CHAT_INFO_CMD",
                chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()),
                chat_type=self.cmd_data.Chat().type,
                chat_id=self.cmd_data.Chat().id,
            )
        )


class UsersListCmd(CommandBase):
    """Command for getting the users list."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the users list command.

        Args:
            **kwargs: Additional keyword arguments
        """
        chat_members = await ChatMembersGetter(self.client).GetAll(self.cmd_data.Chat())
        await self._SendMessage(
            self.translator.GetSentence(
                "USERS_LIST_CMD",
                chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()),
                members_count=chat_members.Count(),
                members_list=str(chat_members),
            )
        )


class InviteLinkCmd(CommandBase):
    """Command for generating a new invite link."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the invite link command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._NewInviteLink()


class VersionCmd(CommandBase):
    """Command for showing bot version."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the version command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(self.translator.GetSentence("VERSION_CMD", version=__version__))


class CheckNoUsernameCmd(CommandBase):
    """Command for checking users with no username."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the check no username command.

        Args:
            **kwargs: Additional keyword arguments
        """
        chat_members = await MembersUsernameGetter(self.client, self.config).GetAllWithNoUsername(self.cmd_data.Chat())

        if chat_members.Any():
            left_hours = self.cmd_data.Params().GetAsInt(0, 0)

            msg = self.translator.GetSentence(
                "CHECK_NO_USERNAME_NOTICE_CMD",
                chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()),
                members_count=chat_members.Count(),
                members_list=str(chat_members),
                hours_left=self.__HoursToStr(left_hours),
            )

            support_email = self.config.GetValue(BotConfigTypes.SUPPORT_EMAIL)
            support_tg = self.config.GetValue(BotConfigTypes.SUPPORT_TELEGRAM)
            if support_email != "" and support_tg != "":
                msg += self.translator.GetSentence(
                    "CHECK_NO_USERNAME_EMAIL_TG_CMD", support_email=support_email, support_telegram=support_tg
                )
            elif support_email != "":
                msg += self.translator.GetSentence("CHECK_NO_USERNAME_ONLY_EMAIL_CMD", support_email=support_email)
            elif support_tg != "":
                msg += self.translator.GetSentence("CHECK_NO_USERNAME_ONLY_TG_CMD", support_telegram=support_tg)
        else:
            msg = self.translator.GetSentence("CHECK_NO_USERNAME_ALL_OK_CMD", chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()))

        await self._SendMessage(msg)

    def __HoursToStr(self,
                     hours: int) -> str:
        """
        Convert hours to a human-readable time string.

        Args:
            hours: Number of hours

        Returns:
            Human-readable time string
        """
        if hours > 47:
            hours_str = self.translator.GetSentence("WITHIN_DAYS_MSG", days=hours // 24)
        elif hours > 1:
            hours_str = self.translator.GetSentence("WITHIN_HOURS_MSG", hours=hours)
        else:
            hours_str = self.translator.GetSentence("ASAP_MSG")
        return hours_str


class RemoveNoUsernameCmd(CommandBase):
    """Command for removing users with no username."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the remove no username command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(
            self.translator.GetSentence("REMOVE_NO_USERNAME_NOTICE_CMD", chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()))
        )

        finished = False
        kicked_members = ChatMembersList()
        while not finished:
            curr_kicked_members = await MembersKicker(self.client, self.config, self.logger).KickAllWithNoUsername(self.cmd_data.Chat())
            if curr_kicked_members.Any():
                kicked_members.AddMultiple(curr_kicked_members)
                finished = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
            else:
                finished = True

        msg = self.translator.GetSentence("REMOVE_NO_USERNAME_COMPLETED_CMD", members_count=kicked_members.Count())
        if kicked_members.Any():
            msg += self.translator.GetSentence("REMOVE_NO_USERNAME_LIST_CMD", members_list=str(kicked_members))

        await self._SendMessage(msg)
        if kicked_members.Any():
            await self._NewInviteLink()


class SetCheckPaymentsOnJoinCmd(CommandBase):
    """Command for setting payment check on joined members."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the set check payments on join command.

        Args:
            **kwargs: Additional keyword arguments
        """
        try:
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            self.config.SetValue(BotConfigTypes.PAYMENT_CHECK_ON_JOIN, flag)

            if self.config.GetValue(BotConfigTypes.PAYMENT_CHECK_ON_JOIN):
                await self._SendMessage(self.translator.GetSentence("SET_CHECK_PAYMENT_ON_JOIN_EN_CMD"))
            else:
                await self._SendMessage(self.translator.GetSentence("SET_CHECK_PAYMENT_ON_JOIN_DIS_CMD"))


class IsCheckPaymentsOnJoinCmd(CommandBase):
    """Command for checking if payment check on joined members is enabled."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the is check payments on join command.

        Args:
            **kwargs: Additional keyword arguments
        """
        if self.config.GetValue(BotConfigTypes.PAYMENT_CHECK_ON_JOIN):
            await self._SendMessage(self.translator.GetSentence("IS_CHECK_PAYMENT_ON_JOIN_EN_CMD"))
        else:
            await self._SendMessage(self.translator.GetSentence("IS_CHECK_PAYMENT_ON_JOIN_DIS_CMD"))


class CheckPaymentsDataCmd(CommandBase):
    """Command for checking payments data for errors."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the check payments data command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(self.translator.GetSentence("CHECK_PAYMENTS_DATA_NOTICE_CMD"))

        payments_loader = PaymentsLoaderFactory(self.config, self.logger).CreateLoader()
        payments_data_err = await payments_loader.CheckForErrors()

        if payments_data_err.Any():
            msg = self.translator.GetSentence("CHECK_PAYMENTS_DATA_COMPLETED_CMD", errors_count=payments_data_err.Count())

            for payment_err in payments_data_err:
                if payment_err.Type() == PaymentErrorTypes.DUPLICATED_DATA_ERR:
                    msg += self.translator.GetSentence("CHECK_PAYMENTS_DATA_DUPLICATED_ERR_CMD", row_index=payment_err.Row())
                elif payment_err.Type() == PaymentErrorTypes.INVALID_DATE_ERR:
                    msg += self.translator.GetSentence(
                        "CHECK_PAYMENTS_DATA_DATE_ERR_CMD",
                        user=payment_err.User(),
                        row_index=payment_err.Row(),
                        expiration_date=payment_err.ExpirationDate(),
                    )
        else:
            msg = self.translator.GetSentence("CHECK_PAYMENTS_DATA_ALL_OK_CMD")

        await self._SendMessage(msg)


class EmailNoPaymentCmd(CommandBase):
    """Command for sending email to users with no payment."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the email no payment command.

        Args:
            **kwargs: Additional keyword arguments
        """
        if not self.config.GetValue(BotConfigTypes.EMAIL_ENABLED):
            msg = self.translator.GetSentence("EMAIL_NO_PAYMENT_DISABLED_CMD")
        else:
            days_left = self.cmd_data.Params().GetAsInt(0, 0)

            await self._SendMessage(
                self.translator.GetSentence("EMAIL_NO_PAYMENT_NOTICE_CMD",
                                            chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()))
            )

            try:
                expired_payments = await PaymentsEmailer(
                    self.client,
                    self.config,
                    self.logger
                ).EmailAllWithExpiringPayment(days_left)

                if expired_payments.Any():
                    days_left_str = (
                        self.translator.GetSentence("IN_DAYS_MSG", days=days_left)
                        if days_left > 1
                        else (self.translator.GetSentence("TOMORROW_MSG") if days_left == 1 else self.translator.GetSentence("TODAY_MSG"))
                    )

                    msg = self.translator.GetSentence(
                        "EMAIL_NO_PAYMENT_COMPLETED_CMD",
                        days_left=days_left_str,
                        members_count=expired_payments.Count(),
                        members_list=str(expired_payments),
                    )
                else:
                    msg = self.translator.GetSentence("EMAIL_NO_PAYMENT_ALL_OK_CMD")
            except SmtpEmailerError:
                self.logger.GetLogger().exception("Error while sending email to no payment members")
                msg = self.translator.GetSentence("EMAIL_NO_PAYMENT_ERR_CMD")

        await self._SendMessage(msg)


class CheckNoPaymentCmd(CommandBase):
    """Command for checking users with no payment."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the check no payment command.

        Args:
            **kwargs: Additional keyword arguments
        """
        days_left = self.cmd_data.Params().GetAsInt(0, 0)
        last_day = self.cmd_data.Params().GetAsInt(1, 0)

        await self._SendMessage(
            self.translator.GetSentence(
                "CHECK_NO_PAYMENT_NOTICE_CMD", chat_title=ChatHelper.GetTitle(self.cmd_data.Chat())
            )
        )

        expired_members = await MembersPaymentGetter(self.client, self.config, self.logger).GetAllMembersWithExpiringPayment(
            self.cmd_data.Chat(), days_left
        )

        if expired_members.Any():
            days_left_str = (
                self.translator.GetSentence("IN_DAYS_MSG", days=days_left)
                if days_left > 1
                else (self.translator.GetSentence("TOMORROW_MSG") if days_left == 1 else self.translator.GetSentence("TODAY_MSG"))
            )
            last_day_str = (
                self.translator.GetSentence("DAY_OF_MONTH_MSG", day_of_month=last_day)
                if 1 <= last_day <= 31
                else self.translator.GetSentence("FEW_DAYS_MSG")
            )

            msg = self.translator.GetSentence(
                "CHECK_NO_PAYMENT_COMPLETED_CMD",
                days_left=days_left_str,
                members_count=expired_members.Count(),
                members_list=str(expired_members),
                last_day=last_day_str,
            )

            website = self.config.GetValue(BotConfigTypes.PAYMENT_WEBSITE)
            if website != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_WEBSITE_CMD", website=website)

            support_email = self.config.GetValue(BotConfigTypes.SUPPORT_EMAIL)
            support_tg = self.config.GetValue(BotConfigTypes.SUPPORT_TELEGRAM)
            if support_email != "" and support_tg != "":
                msg += self.translator.GetSentence(
                    "CHECK_NO_PAYMENT_EMAIL_TG_CMD", support_email=support_email, support_telegram=support_tg
                )
            elif support_email != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_ONLY_EMAIL_CMD", support_email=support_email)
            elif support_tg != "":
                msg += self.translator.GetSentence("CHECK_NO_PAYMENT_ONLY_TG_CMD", support_telegram=support_tg)
        else:
            msg = self.translator.GetSentence("CHECK_NO_PAYMENT_ALL_OK_CMD", chat_title=ChatHelper.GetTitle(self.cmd_data.Chat()))

        await self._SendMessage(msg)


class RemoveNoPaymentCmd(CommandBase):
    """Command for removing users with no payment."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the remove no payment command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await self._SendMessage(
            self.translator.GetSentence(
                "REMOVE_NO_PAYMENT_NOTICE_CMD", chat_title=ChatHelper.GetTitle(self.cmd_data.Chat())
            )
        )

        finished = False
        kicked_members = ChatMembersList()
        while not finished:
            curr_kicked_members = await MembersKicker(self.client, self.config, self.logger).KickAllWithExpiredPayment(self.cmd_data.Chat())
            if curr_kicked_members.Any():
                kicked_members.AddMultiple(curr_kicked_members)
                finished = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
            else:
                finished = True

        msg = self.translator.GetSentence("REMOVE_NO_PAYMENT_COMPLETED_CMD", members_count=kicked_members.Count())
        if kicked_members.Any():
            msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_LIST_CMD", members_list=str(kicked_members))

        await self._SendMessage(msg)
        if kicked_members.Any():
            await self._NewInviteLink()


class PaymentTaskStartCmd(CommandBase):
    """Command for starting payment task."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the payment task start command.

        Args:
            **kwargs: Additional keyword arguments
        """
        try:
            period_hours = self.cmd_data.Params().GetAsInt(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["payments_check_scheduler"].Start(period_hours)
                await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_START_OK_CMD", period=period_hours))
            except PaymentsCheckJobAlreadyRunningError:
                await self._SendMessage(self.translator.GetSentence("TASK_EXISTENT_ERR_MSG"))
            except PaymentsCheckJobInvalidPeriodError:
                await self._SendMessage(self.translator.GetSentence("TASK_PERIOD_ERR_MSG"))


class PaymentTaskStopCmd(CommandBase):
    """Command for stopping payment task."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the payment task stop command.

        Args:
            **kwargs: Additional keyword arguments
        """
        try:
            kwargs["payments_check_scheduler"].Stop()
            await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_STOP_OK_CMD"))
        except PaymentsCheckJobNotRunningError:
            await self._SendMessage(self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG"))


class PaymentTaskAddChatCmd(CommandBase):
    """Command for adding current chat to payment task."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the payment task add chat command.

        Args:
            **kwargs: Additional keyword arguments
        """
        try:
            await kwargs["payments_check_scheduler"].AddChat(self.cmd_data.Chat())
            await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_ADD_CHAT_OK_CMD"))
        except PaymentsCheckJobChatAlreadyPresentError:
            await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_ADD_CHAT_ERR_CMD"))


class PaymentTaskRemoveChatCmd(CommandBase):
    """Command for removing current chat from payment task."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the payment task remove chat command.

        Args:
            **kwargs: Additional keyword arguments
        """
        try:
            await kwargs["payments_check_scheduler"].RemoveChat(self.cmd_data.Chat())
            await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_REMOVE_CHAT_OK_CMD"))
        except PaymentsCheckJobChatNotPresentError:
            await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_REMOVE_CHAT_ERR_CMD"))


class PaymentTaskRemoveAllChatsCmd(CommandBase):
    """Command for removing all chats from payment task."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the payment task remove all chats command.

        Args:
            **kwargs: Additional keyword arguments
        """
        await kwargs["payments_check_scheduler"].RemoveAllChats()
        await self._SendMessage(self.translator.GetSentence("PAYMENT_TASK_REMOVE_ALL_CHATS_CMD"))


class PaymentTaskInfoCmd(CommandBase):
    """Command for getting payment task information."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """
        Execute the payment task info command.

        Args:
            **kwargs: Additional keyword arguments
        """
        is_running = kwargs["payments_check_scheduler"].IsRunning()
        period = kwargs["payments_check_scheduler"].GetPeriod()
        chats = kwargs["payments_check_scheduler"].GetChats()

        state = self.translator.GetSentence("TASK_RUNNING_MSG") if is_running else self.translator.GetSentence("TASK_STOPPED_MSG")

        msg = self.translator.GetSentence("PAYMENT_TASK_INFO_STATE_CMD", state=state)
        if is_running:
            msg += self.translator.GetSentence("PAYMENT_TASK_INFO_PERIOD_CMD", period=period)
        if chats.Any():
            msg += self.translator.GetSentence("PAYMENT_TASK_INFO_GROUPS_CMD", chats_count=chats.Count(), chats_list=str(chats))

        await self._SendMessage(msg)
