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
from typing import Any, Dict, Iterator
from abc import ABC


#
# Classes
#

# Wrapped dict class
class WrappedDict(ABC):
    # Constructor
    def __init__(self) -> None:
        self.dict_elements = {}

    # Add single element
    def AddSingle(self,
                  key: Any,
                  value: Any) -> None:
        self.dict_elements[key] = value

    # Add multiple elements
    def AddMultiple(self,
                    elements: Dict[Any, Any]) -> None:
        self.dict_elements = {**self.dict_elements, **elements}

    # Remove single element
    def RemoveSingle(self,
                     key: Any) -> None:
        self.dict_elements.pop(key, None)

    # Get if key is present
    def IsKey(self,
              key: Any) -> bool:
        return key in self.dict_elements

    # Get if value is present
    def IsValue(self,
                value: Any) -> bool:
        return value in self.dict_elements.values()

    # Clear element
    def Clear(self) -> None:
        self.dict_elements.clear()

    # Get elements count
    def Count(self) -> int:
        return len(self.dict_elements)

    # Get if any
    def Any(self) -> bool:
        return self.Count() > 0

    # Get if empty
    def Empty(self) -> bool:
        return self.Count() == 0

    # Get dict
    def GetDict(self) -> Dict[Any, Any]:
        return self.dict_elements

    # Get iterator
    def __iter__(self) -> Iterator[Any]:
        yield from self.dict_elements
