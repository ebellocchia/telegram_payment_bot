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
from xml.etree import ElementTree
from typing import Optional


#
# Classes
#

# Translation loader class
class TranslationLoader:
    # Default language folder
    DEF_LANG_FOLDER = "lang"
    # Default file name
    DEF_FILE_NAME = "lang_en.xml"
    # XML tag for sentences
    SENTENCE_XML_TAG = "sentence"

    # Constructor
    def __init__(self) -> None:
        self.sentences = {}

    # Load translation file
    def Load(self,
             file_name: Optional[str] = None) -> None:
        file_name = (os.path.join(os.path.dirname(__file__), self.DEF_LANG_FOLDER, self.DEF_FILE_NAME)
                     if file_name is None
                     else file_name)

        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        for child in root:
            if child.tag == self.SENTENCE_XML_TAG:
                self.sentences[child.attrib["id"]] = child.text.replace("\\n", "\n")

    # Get sentence
    def GetSentence(self,
                    sentence_id: str) -> str:
        return self.sentences[sentence_id]
