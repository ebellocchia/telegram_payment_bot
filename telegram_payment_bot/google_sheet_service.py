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
import os
import pickle
from typing import Any, List
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


#
# Classes
#


# Constant for Google sheet service class
class GoogleSheetServiceConst:
    # Scope for authentication
    SCOPES: List[str] = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


# Google sheet service class
class GoogleSheetService:

    # Constructor
    def __init__(self) -> None:
        self.service = None

    # Initialize
    def Init(self,
             credentials_file: str,
             token_file: str) -> None:
        creds = None

        # From Google example: https://developers.google.com/sheets/api/quickstart/python
        #
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, GoogleSheetServiceConst.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, "wb") as token:
                pickle.dump(creds, token)

        self.service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    # Get handle
    def GetHandle(self) -> Any:
        return self.service
