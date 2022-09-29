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
from apscheduler.schedulers.background import BackgroundScheduler

from telegram_payment_bot.bot.bot_config import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.misc.helpers import ChatHelper
from telegram_payment_bot.payment.payments_check_job import PaymentsCheckJob, PaymentsCheckJobChats
from telegram_payment_bot.translator.translation_loader import TranslationLoader


#
# Classes
#

# Job already running error
class PaymentsCheckJobAlreadyRunningError(Exception):
    pass


# Job not running error
class PaymentsCheckJobNotRunningError(Exception):
    pass


# Job invalid period error
class PaymentsCheckJobInvalidPeriodError(Exception):
    pass


# Job chat already present
class PaymentsCheckJobChatAlreadyPresentError(Exception):
    pass


# Job chat not present
class PaymentsCheckJobChatNotPresentError(Exception):
    pass


# Constants for payments check scheduler class
class PaymentsCheckSchedulerConst:
    # Minimum/Maximum periods
    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24
    # Job ID
    JOB_ID: str = "payment_check_job"


# Payments check scheduler class
class PaymentsCheckScheduler:

    config: ConfigObject
    logger: Logger
    payments_checker_job: PaymentsCheckJob
    scheduler: BackgroundScheduler

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.payments_checker_job = PaymentsCheckJob(client, config, logger, translator)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    # Get chats
    def GetChats(self) -> PaymentsCheckJobChats:
        return self.payments_checker_job.GetChats()

    # Get period
    def GetPeriod(self) -> int:
        return self.payments_checker_job.GetPeriod()

    # Start
    def Start(self,
              period_hours: int) -> None:
        # Check if running
        if self.IsRunning():
            self.logger.GetLogger().error("Payments check job already running, cannot start it")
            raise PaymentsCheckJobAlreadyRunningError()

        # Check period
        if (period_hours < PaymentsCheckSchedulerConst.MIN_PERIOD_HOURS or
                period_hours > PaymentsCheckSchedulerConst.MAX_PERIOD_HOURS):
            self.logger.GetLogger().error(
                f"Invalid period {period_hours} for payments check job, cannot start it"
            )
            raise PaymentsCheckJobInvalidPeriodError()

        # Add job
        self.__AddJob(period_hours)

    # Stop
    def Stop(self) -> None:
        if not self.IsRunning():
            self.logger.GetLogger().error("Payments check job not running, cannot stop it")
            raise PaymentsCheckJobNotRunningError()

        self.scheduler.remove_job(PaymentsCheckSchedulerConst.JOB_ID)
        self.logger.GetLogger().info("Stopped payments check job")

    # Add chat
    def AddChat(self,
                chat: pyrogram.types.Chat) -> None:
        if not self.payments_checker_job.AddChat(chat):
            self.logger.GetLogger().error(
                f"Chat {ChatHelper.GetTitleOrId(chat)} already present in payments check job, cannot add it"
            )
            raise PaymentsCheckJobChatAlreadyPresentError()

        self.logger.GetLogger().info(
            f"Added chat {ChatHelper.GetTitleOrId(chat)} to payments check job"
        )

    # Remove chat
    def RemoveChat(self,
                   chat: pyrogram.types.Chat) -> None:
        if not self.payments_checker_job.RemoveChat(chat):
            self.logger.GetLogger().error(
                f"Chat {ChatHelper.GetTitleOrId(chat)} not present in payments check job, cannot remove it"
            )
            raise PaymentsCheckJobChatNotPresentError()

        self.logger.GetLogger().info(
            f"Removed chat {ChatHelper.GetTitleOrId(chat)} from payments check job"
        )

    # Called when chat is left by the bot
    def ChatLeft(self,
                 chat: pyrogram.types.Chat) -> None:
        self.payments_checker_job.RemoveChat(chat)
        self.logger.GetLogger().info(f"Left chat {ChatHelper.GetTitleOrId(chat)}")

    # Remove all chats
    def RemoveAllChats(self) -> None:
        self.payments_checker_job.RemoveAllChats()
        self.logger.GetLogger().info("Removed all chats from payments check job")

    # Get if running
    def IsRunning(self) -> bool:
        return self.scheduler.get_job(PaymentsCheckSchedulerConst.JOB_ID) is not None

    # Add job
    def __AddJob(self,
                 period: int) -> None:
        # Set period
        self.payments_checker_job.SetPeriod(period)
        # Add job
        is_test_mode = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
        if is_test_mode:
            self.scheduler.add_job(self.payments_checker_job.DoJob,
                                   "cron",
                                   minute=self.__BuildCronString(period, is_test_mode),
                                   id=PaymentsCheckSchedulerConst.JOB_ID)
        else:
            self.scheduler.add_job(self.payments_checker_job.DoJob,
                                   "cron",
                                   hour=self.__BuildCronString(period, is_test_mode),
                                   id=PaymentsCheckSchedulerConst.JOB_ID)
        # Log
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(f"Started payments check job (period: {period} {per_sym})")

    # Build cron string
    @staticmethod
    def __BuildCronString(period: int,
                          is_test_mode: bool) -> str:
        max_val = 24 if not is_test_mode else 60
        return ",".join([str(i) for i in range(0, max_val, period)])
