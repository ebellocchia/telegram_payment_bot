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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#
# Classes
#

# SMTP emailer error class
class SmtpEmailerError(Exception):
    pass


# SMTP emailer class
class SmtpEmailer:
    # Constructor
    def __init__(self):
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

    # HTML message getter
    @property
    def HtmlMsg(self) -> str:
        return self.html_msg

    # HTML message setter
    @HtmlMsg.setter
    def HtmlMsg(self,
                html_msg: str) -> None:
        self.html_msg = html_msg

    # Plain message getter
    @property
    def PlainMsg(self) -> str:
        return self.plain_msg

    # Plain message setter
    @PlainMsg.setter
    def PlainMsg(self,
                 plain_msg: str) -> None:
        self.plain_msg = plain_msg

    # Sender getter
    @property
    def From(self) -> str:
        return self.sender

    # Sender setter
    @From.setter
    def From(self,
             sender: str) -> None:
        self.sender = sender

    # Recipient getter
    @property
    def To(self) -> str:
        return self.recipient

    # Recipient setter
    @To.setter
    def To(self,
           recipient: str) -> None:
        self.recipient = recipient

    # Reply-to getter
    @property
    def ReplyTo(self) -> str:
        return self.reply_to

    # Reply-to setter
    @ReplyTo.setter
    def ReplyTo(self,
                reply_to: str) -> None:
        self.reply_to = reply_to

    # Subject getter
    @property
    def Subject(self) -> str:
        return self.subject

    # Subject setter
    @Subject.setter
    def Subject(self,
                subject: str) -> None:
        self.subject = subject

    # Host getter
    @property
    def Host(self) -> str:
        return self.host

    # Host setter
    @Host.setter
    def Host(self,
             host: str) -> None:
        self.host = host

    # User getter
    @property
    def User(self) -> str:
        return self.user

    # User setter
    @User.setter
    def User(self,
             user: str) -> None:
        self.user = user

    # Password getter
    @property
    def Password(self) -> str:
        return self.password

    # Password setter
    @Password.setter
    def Password(self,
                 password: str) -> None:
        self.password = password

    # Prepare message
    def PrepareMsg(self) -> None:
        self.msg = MIMEMultipart("alternative")
        # Set header
        self.msg["From"] = self.sender
        self.msg["To"] = self.recipient
        self.msg["Subject"] = self.subject
        self.msg["Reply-To"] = self.reply_to
        # Set message body
        self.msg.attach(MIMEText(self.plain_msg, "plain"))
        self.msg.attach(MIMEText(self.html_msg, "html"))

    # Connect
    def Connect(self) -> None:
        self.smtp = smtplib.SMTP(self.host)
        if self.user != "":
            self.smtp.login(self.user, self.password)

    # Disconnect
    def Disconnect(self) -> None:
        if self.smtp is None:
            raise SmtpEmailerError("Disconnect called before connecting")

        self.smtp.quit()
        self.smtp = None

    # Send email
    def Send(self) -> None:
        if self.msg is None:
            raise SmtpEmailerError("Send called before preparing message")
        if self.smtp is None:
            raise SmtpEmailerError("Send called before connecting")

        self.smtp.sendmail(self.sender, self.recipient, self.msg.as_string())

    # Quick send email
    def QuickSend(self) -> None:
        self.PrepareMsg()
        self.Connect()
        self.Send()
        self.Disconnect()
