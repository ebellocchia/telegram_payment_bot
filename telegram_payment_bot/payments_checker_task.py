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
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.logger import Logger
from telegram_payment_bot.payments_checker_job import PaymentCheckerChats, PaymentsCheckerJob
from telegram_payment_bot.translation_loader import TranslationLoader


#
# Classes
#

# Task already running error
class PaymentsCheckerTaskAlreadyRunningError(Exception):
    pass


# Task not running error
class PaymentsCheckerTaskNotRunningError(Exception):
    pass


# Task invalid period error
class PaymentsCheckerTaskInvalidPeriodError(Exception):
    pass


# Task chat already present
class PaymentsCheckerTaskChatAlreadyPresentError(Exception):
    pass


# Task chat not present
class PaymentsCheckerTaskChatNotPresentError(Exception):
    pass


# Constants for payments checker task class
class PaymentsCheckerTaskConst:
    # Minimum/Maximum periods
    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24
    # Job ID
    JOB_ID: str = "payment_check"


# Payments checker task class
class PaymentsCheckerTask:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.payment_checker_job = PaymentsCheckerJob(client, config, logger, translator)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    # Get chats
    def GetChats(self) -> PaymentCheckerChats:
        return self.payment_checker_job.GetChats()

    # Get period
    def GetPeriod(self) -> int:
        return self.payment_checker_job.GetPeriod()

    # Start
    def Start(self,
              period_hours: int) -> None:
        # Check if running
        if self.IsRunning():
            self.logger.GetLogger().error("Payment check task already running, cannot start it")
            raise PaymentsCheckerTaskAlreadyRunningError()

        # Check period
        if (period_hours < PaymentsCheckerTaskConst.MIN_PERIOD_HOURS or
                period_hours > PaymentsCheckerTaskConst.MAX_PERIOD_HOURS):
            self.logger.GetLogger().error(f"Invalid period {period_hours} for payment check task, cannot start it")
            raise PaymentsCheckerTaskInvalidPeriodError()

        # Add task
        self.__AddTask(period_hours)

    # Stop
    def Stop(self) -> None:
        if not self.IsRunning():
            self.logger.GetLogger().error("Payment check task not running, cannot stop it")
            raise PaymentsCheckerTaskNotRunningError()

        self.scheduler.remove_job(PaymentsCheckerTaskConst.JOB_ID)
        self.logger.GetLogger().info("Stopped payment check task")

    # Add chat
    def AddChat(self,
                chat: pyrogram.types.Chat) -> None:
        if not self.payment_checker_job.AddChat(chat):
            self.logger.GetLogger().error(f"Chat {chat.id} already present in payment check task, cannot add it")
            raise PaymentsCheckerTaskChatAlreadyPresentError()

        self.logger.GetLogger().info(f"Added chat {chat.id} to payment check task")

    # Remove chat
    def RemoveChat(self,
                   chat: pyrogram.types.Chat) -> None:
        if not self.payment_checker_job.RemoveChat(chat):
            self.logger.GetLogger().error(f"Chat {chat.id} not present in payment check task, cannot remove it")
            raise PaymentsCheckerTaskChatNotPresentError()

        self.logger.GetLogger().info(f"Removed chat {chat.id} from payment check task")

    # Called when chat is left by the bot
    def ChatLeft(self,
                 chat: pyrogram.types.Chat) -> None:
        self.payment_checker_job.RemoveChat(chat)
        self.logger.GetLogger().info(f"Left chat {chat.id}")

    # Remove all chats
    def RemoveAllChats(self) -> None:
        self.payment_checker_job.RemoveAllChats()
        self.logger.GetLogger().info(f"Removed all chats from payment check task")

    # Get if running
    def IsRunning(self) -> bool:
        return self.scheduler.get_job(PaymentsCheckerTaskConst.JOB_ID) is not None

    # Add task
    def __AddTask(self,
                  period: int) -> None:
        # Set period
        self.payment_checker_job.SetPeriod(period)
        # Add job
        is_test_mode = self.config.GetValue(ConfigTypes.APP_TEST_MODE)
        if is_test_mode:
            self.scheduler.add_job(self.payment_checker_job.CheckPayments,
                                   "cron",
                                   minute=self.__BuildCronString(period, is_test_mode),
                                   id=PaymentsCheckerTaskConst.JOB_ID)
        else:
            self.scheduler.add_job(self.payment_checker_job.CheckPayments,
                                   "cron",
                                   hour=self.__BuildCronString(period, is_test_mode),
                                   id=PaymentsCheckerTaskConst.JOB_ID)
        # Log
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(f"Started payment check task (period: {period} {per_sym})")

    # Build cron string
    @staticmethod
    def __BuildCronString(period: int,
                          is_test_mode: bool) -> str:
        max_val = 24 if not is_test_mode else 60

        cron_str = ""
        for i in range(0, max_val, period):
            cron_str += f"{i},"

        return cron_str[:-1]
