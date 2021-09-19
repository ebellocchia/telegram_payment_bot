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
from telegram_payment_bot.members_kicker import MembersKicker
from telegram_payment_bot.message_sender import MessageSender
from telegram_payment_bot.translation_loader import TranslationLoader


#
# Classes
#

# Constants for payments periodic checker class
class PaymentsPeriodicCheckerConst:
    # Minimum period in minutes
    MIN_PERIOD_MINUTE: int = 1
    # Job ID
    JOB_ID: str = "payment_check"

    # Scheduler states
    STATE_STOPPED = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

# Payments periodic checker class
class PaymentsPeriodicChecker:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.members_kicker = MembersKicker(self.client, self.config, self.logger)
        self.message_sender = MessageSender(client, config, logger)
        self.scheduler = BackgroundScheduler()

    # Initialize
    def Init(self) -> None:
        if self.__IsJobPresent():
            self.logger.GetLogger().error("Payment check task has been already initialized")
            return

        check_period_min = self.config.GetValue(ConfigTypes.PAYMENT_CHECK_PERIOD_MIN)
        if check_period_min >= PaymentsPeriodicCheckerConst.MIN_PERIOD_MINUTE:
            self.logger.GetLogger().info("Payment check task initialized (period: %d min)" % check_period_min)
            self.scheduler.add_job(self.__PaymentsCheckTask,
                                   "interval",
                                   minutes=check_period_min,
                                   id=PaymentsPeriodicCheckerConst.JOB_ID)
            self.scheduler.start(paused=True)
        else:
            self.logger.GetLogger().info("Payment check task disabled (invalid period)")

    # Start
    def Start(self) -> None:
        if not self.__IsJobPresent():
            self.logger.GetLogger().error("Payment check task not initialized, unable to start it")
            return

        if self.IsRunning():
            self.logger.GetLogger().error("Payment check task already running")
            return

        self.logger.GetLogger().info("Payment check task started")
        self.scheduler.resume()

    # Stop
    def Stop(self) -> None:
        if not self.__IsJobPresent():
            self.logger.GetLogger().error("Payment check task not initialized, unable to stop it")
            return

        if not self.IsRunning():
            self.logger.GetLogger().error("Payment check task not running")
            return

        # Just pause it without removing the job
        self.logger.GetLogger().info("Payment check task stopped")
        self.scheduler.pause()

    # Get if running
    def IsRunning(self) -> bool:
        return self.scheduler.state == PaymentsPeriodicCheckerConst.STATE_RUNNING

    # Get if job is present
    def __IsJobPresent(self) -> bool:
        return self.scheduler.get_job(PaymentsPeriodicCheckerConst.JOB_ID) is not None

    # Payment check task
    def __PaymentsCheckTask(self) -> None:
        # Log
        self.logger.GetLogger().info("Periodic payments check started")

        # Kick members for each chat
        for chat_id in self.config.GetValue(ConfigTypes.PAYMENT_CHECK_CHAT_IDS):
            # Kick members
            self.logger.GetLogger().info("Checking payments for chat ID %d..." % chat_id)
            curr_chat = pyrogram.types.Chat(id=chat_id, type="supergroup")
            kicked_members = self.members_kicker.KickAllWithExpiredPayment(curr_chat)

            # Log kicked members
            self.logger.GetLogger().info("Kicked members for chat ID %d: %d" % (chat_id, kicked_members.Count()))
            if kicked_members.Any():
                self.logger.GetLogger().info(kicked_members.ToString())

                # Inform authorized users
                msg = self.translator.GetSentence("REMOVE_NO_PAYMENT_P1_CMD") % chat_id
                msg += "\n" + self.translator.GetSentence("REMOVE_NO_PAYMENT_P2_CMD") % kicked_members.Count()
                msg += self.translator.GetSentence("REMOVE_NO_PAYMENT_P3_CMD") % kicked_members.ToString()

                self.message_sender.SendMessageToAuthUsers(curr_chat, msg)
