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

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.email.smtp_emailer import SmtpEmailer


class SubscriptionEmailer:
    """Subscription emailer class."""

    smtp_emailer: SmtpEmailer

    def __init__(self,
                 config: ConfigObject):
        """Constructor."""
        self.smtp_emailer = SmtpEmailer()
        self.smtp_emailer.AuthenticationType = config.GetValue(BotConfigTypes.EMAIL_AUTH_TYPE)
        self.smtp_emailer.From = config.GetValue(BotConfigTypes.EMAIL_FROM)
        self.smtp_emailer.ReplyTo = config.GetValue(BotConfigTypes.EMAIL_REPLY_TO)
        self.smtp_emailer.Subject = config.GetValue(BotConfigTypes.EMAIL_SUBJECT)
        self.smtp_emailer.HtmlMsg = config.GetValue(BotConfigTypes.EMAIL_HTML_BODY)
        self.smtp_emailer.PlainMsg = config.GetValue(BotConfigTypes.EMAIL_ALT_BODY)
        self.smtp_emailer.Host = config.GetValue(BotConfigTypes.EMAIL_HOST)
        self.smtp_emailer.User = config.GetValue(BotConfigTypes.EMAIL_USER)
        self.smtp_emailer.Password = config.GetValue(BotConfigTypes.EMAIL_PASSWORD)

    def PrepareMsg(self,
                   recipient: str) -> None:
        """Prepare message."""
        self.smtp_emailer.To = recipient
        self.smtp_emailer.PrepareMsg()

    async def Connect(self) -> None:
        """Connect."""
        await self.smtp_emailer.Connect()

    async def Disconnect(self) -> None:
        """Disconnect."""
        await self.smtp_emailer.Disconnect()

    async def Send(self) -> None:
        """Send email."""
        await self.smtp_emailer.Send()

    async def QuickSend(self,
                        recipient: str) -> None:
        """Quick send email."""
        self.smtp_emailer.To = recipient
        await self.smtp_emailer.QuickSend()
