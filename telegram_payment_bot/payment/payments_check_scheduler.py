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

import pyrogram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.helpers import ChatHelper
from telegram_payment_bot.payment.payments_check_job import PaymentsCheckJob, PaymentsCheckJobChats
from telegram_payment_bot.translator.translation_loader import TranslationLoader


class PaymentsCheckJobAlreadyRunningError(Exception):
    """Exception raised when trying to start a job that is already running."""


class PaymentsCheckJobNotRunningError(Exception):
    """Exception raised when trying to stop a job that is not running."""


class PaymentsCheckJobInvalidPeriodError(Exception):
    """Exception raised when an invalid job period is specified."""


class PaymentsCheckJobChatAlreadyPresentError(Exception):
    """Exception raised when trying to add a chat that is already present."""


class PaymentsCheckJobChatNotPresentError(Exception):
    """Exception raised when trying to remove a chat that is not present."""


class PaymentsCheckSchedulerConst:
    """Constants for payments check scheduler class."""

    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24
    JOB_ID: str = "payment_check_job"


class PaymentsCheckScheduler:
    """Scheduler for periodic payments check job."""

    config: ConfigObject
    logger: Logger
    payments_checker_job: PaymentsCheckJob
    scheduler: AsyncIOScheduler

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the payments check scheduler.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader instance
        """
        self.config = config
        self.logger = logger
        self.payments_checker_job = PaymentsCheckJob(client, config, logger, translator)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def GetChats(self) -> PaymentsCheckJobChats:
        """Get the chats in the job.

        Returns:
            PaymentsCheckJobChats containing all chats
        """
        return self.payments_checker_job.GetChats()

    def GetPeriod(self) -> int:
        """Get the job period.

        Returns:
            Job period in hours
        """
        return self.payments_checker_job.GetPeriod()

    def Start(self,
              period_hours: int) -> None:
        """Start the payments check job.

        Args:
            period_hours: Job period in hours

        Raises:
            PaymentsCheckJobAlreadyRunningError: If job is already running
            PaymentsCheckJobInvalidPeriodError: If period is invalid
        """
        if self.IsRunning():
            self.logger.GetLogger().error("Payments check job already running, cannot start it")
            raise PaymentsCheckJobAlreadyRunningError()

        if (period_hours < PaymentsCheckSchedulerConst.MIN_PERIOD_HOURS or
                period_hours > PaymentsCheckSchedulerConst.MAX_PERIOD_HOURS):
            self.logger.GetLogger().error(
                f"Invalid period {period_hours} for payments check job, cannot start it"
            )
            raise PaymentsCheckJobInvalidPeriodError()

        self.__AddJob(period_hours)

    def Stop(self) -> None:
        """Stop the payments check job.

        Raises:
            PaymentsCheckJobNotRunningError: If job is not running
        """
        if not self.IsRunning():
            self.logger.GetLogger().error("Payments check job not running, cannot stop it")
            raise PaymentsCheckJobNotRunningError()

        self.scheduler.remove_job(PaymentsCheckSchedulerConst.JOB_ID)
        self.logger.GetLogger().info("Stopped payments check job")

    async def AddChat(self,
                      chat: pyrogram.types.Chat) -> None:
        """Add a chat to the job.

        Args:
            chat: Chat to add

        Raises:
            PaymentsCheckJobChatAlreadyPresentError: If chat is already present
        """
        if not await self.payments_checker_job.AddChat(chat):
            self.logger.GetLogger().error(
                f"Chat {ChatHelper.GetTitleOrId(chat)} already present in payments check job, cannot add it"
            )
            raise PaymentsCheckJobChatAlreadyPresentError()

        self.logger.GetLogger().info(
            f"Added chat {ChatHelper.GetTitleOrId(chat)} to payments check job"
        )

    async def RemoveChat(self,
                         chat: pyrogram.types.Chat) -> None:
        """Remove a chat from the job.

        Args:
            chat: Chat to remove

        Raises:
            PaymentsCheckJobChatNotPresentError: If chat is not present
        """
        if not await self.payments_checker_job.RemoveChat(chat):
            self.logger.GetLogger().error(
                f"Chat {ChatHelper.GetTitleOrId(chat)} not present in payments check job, cannot remove it"
            )
            raise PaymentsCheckJobChatNotPresentError()

        self.logger.GetLogger().info(
            f"Removed chat {ChatHelper.GetTitleOrId(chat)} from payments check job"
        )

    async def ChatLeft(self,
                       chat: pyrogram.types.Chat) -> None:
        """Handle bot leaving a chat.

        Args:
            chat: Chat that was left
        """
        await self.payments_checker_job.RemoveChat(chat)
        self.logger.GetLogger().info(f"Left chat {ChatHelper.GetTitleOrId(chat)}")

    async def RemoveAllChats(self) -> None:
        """Remove all chats from the job."""
        await self.payments_checker_job.RemoveAllChats()
        self.logger.GetLogger().info("Removed all chats from payments check job")

    def IsRunning(self) -> bool:
        """Check if the job is running.

        Returns:
            True if running, False otherwise
        """
        return self.scheduler.get_job(PaymentsCheckSchedulerConst.JOB_ID) is not None

    def __AddJob(self,
                 period: int) -> None:
        """Add the job to the scheduler.

        Args:
            period: Job period in hours
        """
        self.payments_checker_job.SetPeriod(period)
        is_test_mode = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
        cron_str = self.__BuildCronString(period, is_test_mode)
        if is_test_mode:
            self.scheduler.add_job(self.payments_checker_job.DoJob,
                                   "cron",
                                   minute=cron_str,
                                   id=PaymentsCheckSchedulerConst.JOB_ID)
        else:
            self.scheduler.add_job(self.payments_checker_job.DoJob,
                                   "cron",
                                   hour=cron_str,
                                   id=PaymentsCheckSchedulerConst.JOB_ID)
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(
            f"Started payments check job (period: {period} {per_sym}, cron: {cron_str})"
        )

    @staticmethod
    def __BuildCronString(period: int,
                          is_test_mode: bool) -> str:
        """Build a cron string for the job period.

        Args:
            period: Job period
            is_test_mode: True if in test mode (uses minutes), False for production (uses hours)

        Returns:
            Cron string
        """
        max_val = 24 if not is_test_mode else 60
        return ",".join([str(i) for i in range(0, max_val, period)])
