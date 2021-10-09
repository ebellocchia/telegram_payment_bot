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
import time


#
# Classes
#

# Constants for ban helper class
class BanHelperConst:
    # Kick time in seconds
    KICK_TIME_SEC: int = 60


# Ban helper class
class BanHelper:

    client: pyrogram.Client

    # Constructor
    def __init__(self,
                 client: pyrogram.Client) -> None:
        self.client = client

    # Ban user
    def BanUser(self,
                chat: pyrogram.types.Chat,
                user: pyrogram.types.User) -> None:
        self.client.kick_chat_member(chat.id, user.id)

    # Kick user
    def KickUser(self,
                 chat: pyrogram.types.Chat,
                 user: pyrogram.types.User) -> None:
        # Ban only for 1 minute, so they can join again with an invite link if necessary
        # (otherwise they cannot join anymore, unless manually added to the group)
        self.client.kick_chat_member(chat.id, user.id, int(time.time() + BanHelperConst.KICK_TIME_SEC))

    # Unban user
    def UnbanUser(self,
                  chat: pyrogram.types.Chat,
                  user: pyrogram.types.User) -> None:
        self.client.unban_chat_member(chat.id, user.id)
