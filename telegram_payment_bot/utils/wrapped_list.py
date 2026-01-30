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
from typing import Callable, Iterator, List, Optional, Union


class WrappedList(ABC):
    """Wrapped list class with enhanced functionality."""

    list_elements: List[typing.Any]

    def __init__(self) -> None:
        """Constructor."""
        self.list_elements = []

    def AddSingle(self,
                  element: typing.Any) -> None:
        """
        Add single element.

        Args:
            element: Element to add
        """
        self.list_elements.append(element)

    def AddMultiple(self,
                    elements: Union[List[typing.Any], WrappedList]) -> None:
        """
        Add multiple elements.

        Args:
            elements: List or WrappedList containing elements to add
        """
        if isinstance(elements, WrappedList):
            self.list_elements.extend(elements.GetList())
        else:
            self.list_elements.extend(elements)

    def RemoveSingle(self,
                     element: typing.Any) -> None:
        """
        Remove single element.

        Args:
            element: Element to remove
        """
        self.list_elements.remove(element)

    def IsElem(self,
               element: typing.Any) -> bool:
        """
        Check if element is present.

        Args:
            element: Element to check

        Returns:
            True if element exists, False otherwise
        """
        return element in self.list_elements

    def Clear(self) -> None:
        """Clear all elements."""
        self.list_elements.clear()

    def Count(self) -> int:
        """
        Get elements count.

        Returns:
            Number of elements
        """
        return len(self.list_elements)

    def Any(self) -> bool:
        """
        Check if any elements exist.

        Returns:
            True if list is not empty, False otherwise
        """
        return self.Count() > 0

    def Empty(self) -> bool:
        """
        Check if list is empty.

        Returns:
            True if list is empty, False otherwise
        """
        return self.Count() == 0

    def Sort(self,
             key: Optional[Callable[[typing.Any], typing.Any]] = None,
             reverse: bool = False) -> None:
        """
        Sort the list.

        Args:
            key: Optional key function for sorting
            reverse: If True, sort in descending order
        """
        self.list_elements.sort(key=key, reverse=reverse)

    def GetList(self) -> List[typing.Any]:
        """
        Get the underlying list.

        Returns:
            The list
        """
        return self.list_elements

    def __getitem__(self,
                    key: int):
        """
        Get item by index.

        Args:
            key: Index to retrieve

        Returns:
            Element at the index
        """
        return self.list_elements[key]

    def __delitem__(self,
                    key: int):
        """
        Delete item by index.

        Args:
            key: Index to delete
        """
        del self.list_elements[key]

    def __setitem__(self,
                    key: int,
                    value: typing.Any):
        """
        Set item by index.

        Args:
            key: Index to set
            value: Value to set
        """
        self.list_elements[key] = value

    def __iter__(self) -> Iterator[typing.Any]:
        """
        Get iterator over elements.

        Returns:
            Iterator over list elements
        """
        yield from self.list_elements
