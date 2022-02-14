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
from __future__ import annotations
from abc import ABC
import typing
from collections.abc import KeysView, ValuesView, ItemsView
from typing import Dict, Iterator, Union


#
# Classes
#

# Wrapped dict class
class WrappedDict(ABC):

    dict_elements: Dict[typing.Any, typing.Any]

    # Constructor
    def __init__(self) -> None:
        self.dict_elements = {}

    # Add single element
    def AddSingle(self,
                  key: typing.Any,
                  value: typing.Any) -> None:
        self.dict_elements[key] = value

    # Add multiple elements
    def AddMultiple(self,
                    elements: Union[Dict[typing.Any, typing.Any], WrappedDict]) -> None:
        if isinstance(elements, WrappedDict):
            self.dict_elements = {**self.dict_elements, **elements.GetDict()}
        else:
            self.dict_elements = {**self.dict_elements, **elements}

    # Remove single element
    def RemoveSingle(self,
                     key: typing.Any) -> None:
        self.dict_elements.pop(key, None)

    # Get if key is present
    def IsKey(self,
              key: typing.Any) -> bool:
        return key in self.dict_elements

    # Get if value is present
    def IsValue(self,
                value: typing.Any) -> bool:
        return value in self.dict_elements.values()

    # Get keys
    def Keys(self) -> KeysView:
        return self.dict_elements.keys()

    # Get values
    def Values(self) -> ValuesView:
        return self.dict_elements.values()

    # Get items
    def Items(self) -> ItemsView:
        return self.dict_elements.items()

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
    def GetDict(self) -> Dict[typing.Any, typing.Any]:
        return self.dict_elements

    # Get item
    def __getitem__(self,
                    key: typing.Any):
        return self.dict_elements[key]

    # Delete item
    def __delitem__(self,
                    key: typing.Any):
        del self.dict_elements[key]

    # Set item
    def __setitem__(self,
                    key: typing.Any,
                    value: typing.Any):
        self.dict_elements[key] = value

    # Get iterator
    def __iter__(self) -> Iterator[typing.Any]:
        yield from self.dict_elements
