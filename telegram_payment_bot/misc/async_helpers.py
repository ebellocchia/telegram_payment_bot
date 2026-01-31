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

"""Async helper functions for compatibility across Python versions."""

import asyncio
import functools
import sys
from typing import Any, Callable, TypeVar


T = TypeVar("T")


if sys.version_info >= (3, 9):
    # Python 3.9+ has asyncio.to_thread
    to_thread = asyncio.to_thread
else:
    # Python 3.8 compatibility: use run_in_executor
    async def to_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Run a blocking function in a thread pool executor.

        Compatible with Python 3.8+. Uses asyncio.to_thread() on Python 3.9+,
        and run_in_executor() on Python 3.8.

        Args:
            func: Function to run in a thread
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The return value of the function
        """
        loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, **kwargs) if kwargs else func
        return await loop.run_in_executor(None, pfunc, *args)
