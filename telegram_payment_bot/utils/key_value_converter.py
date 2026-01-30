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

from typing import Any, Dict


class KeyValueConverter:
    """Key-Value converter for bidirectional dictionary lookups."""

    kv_dict: Dict[str, Any]

    def __init__(self,
                 kv_dict: Dict[str, Any]) -> None:
        """
        Constructor.

        Args:
            kv_dict: Dictionary for key-value conversion
        """
        self.kv_dict = kv_dict

    def KeyToValue(self,
                   key: str) -> Any:
        """
        Convert key to value.

        Args:
            key: Key to look up

        Returns:
            Value associated with the key
        """
        return self.kv_dict[key]

    def ValueToKey(self,
                   value: Any) -> str:
        """
        Convert value to key.

        Args:
            value: Value to look up

        Returns:
            Key associated with the value
        """
        idx = list(self.kv_dict.values()).index(value)
        return list(self.kv_dict.keys())[idx]
