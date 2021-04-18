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
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.smtp_emailer import SmtpEmailer


#
# Classes
#


# Subscription emailer class
class SubscriptionEmailer:
    # Constructor
    def __init__(self,
                 config: Config):
        self.smtp_emailer = SmtpEmailer()
        self.smtp_emailer.From = config.GetValue(ConfigTypes.EMAIL_FROM)
        self.smtp_emailer.ReplyTo = config.GetValue(ConfigTypes.EMAIL_REPLY_TO)
        self.smtp_emailer.Subject = config.GetValue(ConfigTypes.EMAIL_SUBJECT)
        self.smtp_emailer.HtmlMsg = config.GetValue(ConfigTypes.EMAIL_HTML_BODY)
        self.smtp_emailer.PlainMsg = config.GetValue(ConfigTypes.EMAIL_ALT_BODY)
        self.smtp_emailer.Host = config.GetValue(ConfigTypes.EMAIL_HOST)
        self.smtp_emailer.User = config.GetValue(ConfigTypes.EMAIL_USER)
        self.smtp_emailer.Password = config.GetValue(ConfigTypes.EMAIL_PASSWORD)

    # Prepare message
    def PrepareMsg(self,
                   recipient: str) -> None:
        self.smtp_emailer.To = recipient
        self.smtp_emailer.PrepareMsg()

    # Connect
    def Connect(self) -> None:
        self.smtp_emailer.Connect()

    # Disconnect
    def Disconnect(self) -> None:
        self.smtp_emailer.Disconnect()

    # Send email
    def Send(self) -> None:
        self.smtp_emailer.Send()

    # Quick send email
    def QuickSend(self,
                  recipient: str) -> None:
        self.smtp_emailer.To = recipient
        self.smtp_emailer.QuickSend()
