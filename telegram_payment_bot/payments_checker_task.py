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
from telegram_payment_bot.payments_checker_job import PaymentsCheckerJob
from telegram_payment_bot.translation_loader import TranslationLoader


#
# Classes
#

# Constants for payments checker task class
class PaymentsCheckerTaskConst:
    # Minimum period in minutes
    MIN_PERIOD_MINUTE: int = 1
    # Job ID
    JOB_ID: str = "payment_check"

    # Scheduler states
    STATE_STOPPED = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2


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
        self.__Init()

    # Start
    def Start(self) -> None:
        if not self.__IsJobPresent():
            self.logger.GetLogger().error("Payment check task disabled, unable to start it")
            return

        if self.IsRunning():
            self.logger.GetLogger().error("Payment check task already running")
            return

        self.logger.GetLogger().info("Payment check task started")
        self.scheduler.resume()

    # Stop
    def Stop(self) -> None:
        if not self.__IsJobPresent():
            self.logger.GetLogger().error("Payment check task disabled, unable to stop it")
            return

        if not self.IsRunning():
            self.logger.GetLogger().error("Payment check task not running")
            return

        # Just pause it without removing the job
        self.logger.GetLogger().info("Payment check task stopped")
        self.scheduler.pause()

    # Get if running
    def IsRunning(self) -> bool:
        return self.scheduler.state == PaymentsCheckerTaskConst.STATE_RUNNING

    # Initialize
    def __Init(self) -> None:
        check_period_min = self.config.GetValue(ConfigTypes.PAYMENT_CHECK_PERIOD_MIN)
        if check_period_min >= PaymentsCheckerTaskConst.MIN_PERIOD_MINUTE:
            self.logger.GetLogger().info("Payment check task initialized (period: %d min)" % check_period_min)
            self.scheduler.add_job(lambda: self.payment_checker_job.CheckPayments(),
                                   "interval",
                                   minutes=check_period_min,
                                   id=PaymentsCheckerTaskConst.JOB_ID)
            self.scheduler.start(paused=True)
        else:
            self.logger.GetLogger().info("Payment check task disabled (invalid period)")

    # Get if job is present
    def __IsJobPresent(self) -> bool:
        return self.scheduler.get_job(PaymentsCheckerTaskConst.JOB_ID) is not None
