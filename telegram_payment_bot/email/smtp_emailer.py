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

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

from telegram_payment_bot.email.emailer_auth_types import EmailerAuthenticationTypes


class SmtpEmailerError(Exception):
    """SMTP emailer error class."""


class SmtpEmailer:
    """SMTP emailer class."""

    auth_type: EmailerAuthenticationTypes
    html_msg: str
    plain_msg: str
    subject: str
    sender: str
    recipient: str
    reply_to: str
    host: str
    user: str
    password: str
    msg: Optional[MIMEMultipart]
    smtp: Optional[aiosmtplib.SMTP]

    def __init__(self):
        """Constructor."""
        self.auth_type = EmailerAuthenticationTypes.NONE
        self.html_msg = ""
        self.plain_msg = ""
        self.subject = ""
        self.sender = ""
        self.recipient = ""
        self.reply_to = ""
        self.host = ""
        self.user = ""
        self.password = ""
        self.msg = None
        self.smtp = None

    @property
    def AuthenticationType(self) -> EmailerAuthenticationTypes:
        """Authentication type getter."""
        return self.auth_type

    @AuthenticationType.setter
    def AuthenticationType(self,
                           auth_type: EmailerAuthenticationTypes) -> None:
        """Authentication type setter."""
        self.auth_type = auth_type

    @property
    def HtmlMsg(self) -> str:
        """HTML message getter."""
        return self.html_msg

    @HtmlMsg.setter
    def HtmlMsg(self,
                html_msg: str) -> None:
        """HTML message setter."""
        self.html_msg = html_msg

    @property
    def PlainMsg(self) -> str:
        """Plain message getter."""
        return self.plain_msg

    @PlainMsg.setter
    def PlainMsg(self,
                 plain_msg: str) -> None:
        """Plain message setter."""
        self.plain_msg = plain_msg

    @property
    def From(self) -> str:
        """Sender getter."""
        return self.sender

    @From.setter
    def From(self,
             sender: str) -> None:
        """Sender setter."""
        self.sender = sender

    @property
    def To(self) -> str:
        """Recipient getter."""
        return self.recipient

    @To.setter
    def To(self,
           recipient: str) -> None:
        """Recipient setter."""
        self.recipient = recipient

    @property
    def ReplyTo(self) -> str:
        """Reply-to getter."""
        return self.reply_to

    @ReplyTo.setter
    def ReplyTo(self,
                reply_to: str) -> None:
        """Reply-to setter."""
        self.reply_to = reply_to

    @property
    def Subject(self) -> str:
        """Subject getter."""
        return self.subject

    @Subject.setter
    def Subject(self,
                subject: str) -> None:
        """Subject setter."""
        self.subject = subject

    @property
    def Host(self) -> str:
        """Host getter."""
        return self.host

    @Host.setter
    def Host(self,
             host: str) -> None:
        """Host setter."""
        self.host = host

    @property
    def User(self) -> str:
        """User getter."""
        return self.user

    @User.setter
    def User(self,
             user: str) -> None:
        """User setter."""
        self.user = user

    @property
    def Password(self) -> str:
        """Password getter."""
        return self.password

    @Password.setter
    def Password(self,
                 password: str) -> None:
        """Password setter."""
        self.password = password

    def PrepareMsg(self) -> None:
        """Prepare message."""
        self.msg = MIMEMultipart("alternative")
        # Set header
        self.msg["From"] = self.sender
        self.msg["To"] = self.recipient
        self.msg["Subject"] = self.subject
        self.msg["Reply-To"] = self.reply_to
        # Set message body
        self.msg.attach(MIMEText(self.plain_msg, "plain"))
        self.msg.attach(MIMEText(self.html_msg, "html"))

    async def Connect(self) -> None:
        """Connect."""
        try:
            if self.auth_type == EmailerAuthenticationTypes.SSL_TLS:
                self.smtp = aiosmtplib.SMTP(hostname=self.host, port=465, use_tls=True)
                await self.smtp.connect()
                await self.smtp.login(self.user, self.password)
            elif self.auth_type == EmailerAuthenticationTypes.STARTTLS:
                self.smtp = aiosmtplib.SMTP(hostname=self.host, port=587)
                await self.smtp.connect()
                await self.smtp.starttls()
                await self.smtp.login(self.user, self.password)
            else:
                self.smtp = aiosmtplib.SMTP(hostname=self.host)
                await self.smtp.connect()
        except aiosmtplib.SMTPException as ex:
            raise SmtpEmailerError("Error while connecting") from ex

    async def Disconnect(self) -> None:
        """Disconnect."""
        if self.smtp is None:
            raise SmtpEmailerError("Disconnect called before connecting")

        try:
            await self.smtp.quit()
            self.smtp = None
        except aiosmtplib.SMTPException as ex:
            raise SmtpEmailerError("Error while disconnecting") from ex

    async def Send(self) -> None:
        """Send email."""
        if self.msg is None:
            raise SmtpEmailerError("Send called before preparing message")
        if self.smtp is None:
            raise SmtpEmailerError("Send called before connecting")

        try:
            await self.smtp.sendmail(self.sender, self.recipient, self.msg.as_string())
        except aiosmtplib.SMTPException as ex:
            raise SmtpEmailerError("Error while sending email") from ex

    async def QuickSend(self) -> None:
        """Quick send email."""
        self.PrepareMsg()
        await self.Connect()
        await self.Send()
        await self.Disconnect()
