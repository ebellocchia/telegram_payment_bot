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

from __future__ import annotations

import typing
from abc import ABC
from collections.abc import ItemsView, KeysView, ValuesView
from typing import Dict, Iterator, Union


class WrappedDict(ABC):
    """Wrapped dictionary class with enhanced functionality."""

    dict_elements: Dict[typing.Any, typing.Any]

    def __init__(self) -> None:
        """Constructor."""
        self.dict_elements = {}

    def AddSingle(self,
                  key: typing.Any,
                  value: typing.Any) -> None:
        """
        Add single element.

        Args:
            key: Key for the element
            value: Value for the element
        """
        self.dict_elements[key] = value

    def AddMultiple(self,
                    elements: Union[Dict[typing.Any, typing.Any], WrappedDict]) -> None:
        """
        Add multiple elements.

        Args:
            elements: Dictionary or WrappedDict containing elements to add
        """
        if isinstance(elements, WrappedDict):
            self.dict_elements = {**self.dict_elements, **elements.GetDict()}
        else:
            self.dict_elements = {**self.dict_elements, **elements}

    def RemoveSingle(self,
                     key: typing.Any) -> None:
        """
        Remove single element.

        Args:
            key: Key to remove
        """
        self.dict_elements.pop(key, None)

    def IsKey(self,
              key: typing.Any) -> bool:
        """
        Check if key is present.

        Args:
            key: Key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.dict_elements

    def IsValue(self,
                value: typing.Any) -> bool:
        """
        Check if value is present.

        Args:
            value: Value to check

        Returns:
            True if value exists, False otherwise
        """
        return value in self.dict_elements.values()

    def Keys(self) -> KeysView:
        """
        Get keys.

        Returns:
            View of dictionary keys
        """
        return self.dict_elements.keys()

    def Values(self) -> ValuesView:
        """
        Get values.

        Returns:
            View of dictionary values
        """
        return self.dict_elements.values()

    def Items(self) -> ItemsView:
        """
        Get items.

        Returns:
            View of dictionary items
        """
        return self.dict_elements.items()

    def Clear(self) -> None:
        """Clear all elements."""
        self.dict_elements.clear()

    def Count(self) -> int:
        """
        Get elements count.

        Returns:
            Number of elements
        """
        return len(self.dict_elements)

    def Any(self) -> bool:
        """
        Check if any elements exist.

        Returns:
            True if dictionary is not empty, False otherwise
        """
        return self.Count() > 0

    def Empty(self) -> bool:
        """
        Check if dictionary is empty.

        Returns:
            True if dictionary is empty, False otherwise
        """
        return self.Count() == 0

    def GetDict(self) -> Dict[typing.Any, typing.Any]:
        """
        Get the underlying dictionary.

        Returns:
            The dictionary
        """
        return self.dict_elements

    def __getitem__(self,
                    key: typing.Any):
        """
        Get item by key.

        Args:
            key: Key to retrieve

        Returns:
            Value associated with the key
        """
        return self.dict_elements[key]

    def __delitem__(self,
                    key: typing.Any):
        """
        Delete item by key.

        Args:
            key: Key to delete
        """
        del self.dict_elements[key]

    def __setitem__(self,
                    key: typing.Any,
                    value: typing.Any):
        """
        Set item by key.

        Args:
            key: Key to set
            value: Value to set
        """
        self.dict_elements[key] = value

    def __iter__(self) -> Iterator[typing.Any]:
        """
        Get iterator over keys.

        Returns:
            Iterator over dictionary keys
        """
        yield from self.dict_elements
