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


class Utils:
    """Wrapper for utility functions."""

    @staticmethod
    def StrToBool(s: str) -> bool:
        """
        Convert string to boolean.

        Args:
            s: String to convert

        Returns:
            Boolean value

        Raises:
            ValueError: If string is not a valid boolean representation
        """
        s = s.lower()
        if s in ["true", "on", "yes", "y"]:
            return True
        if s in ["false", "off", "no", "n"]:
            return False
        raise ValueError("Invalid string")

    @staticmethod
    def StrToFloat(s: str) -> float:
        """
        Convert string to float.

        Args:
            s: String to convert

        Returns:
            Float value
        """
        return float(s)

    @staticmethod
    def StrToInt(s: str) -> int:
        """
        Convert string to integer.

        Args:
            s: String to convert

        Returns:
            Integer value
        """
        return int(s)
