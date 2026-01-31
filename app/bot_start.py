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

import argparse
import asyncio

from telegram_payment_bot import PaymentBot, __version__


DEF_CONFIG_FILE = "conf/config.ini"


class ArgumentsParser:
    """Argument parser for bot startup."""

    parser: argparse.ArgumentParser

    def __init__(self) -> None:
        """Constructor."""
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-c", "--config",
            type=str,
            default=DEF_CONFIG_FILE,
            help="configuration file"
        )

    def Parse(self) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Returns:
            Parsed arguments namespace
        """
        return self.parser.parse_args()


def print_header() -> None:
    """Print application header with version information."""
    print("")
    print("**********************************")
    print("****                          ****")
    print("***                            ***")
    print("**                              **")
    print("*      Telegram Payment Bot      *")
    print("*   Author: Emanuele Bellocchia  *")
    print(f"*         Version: {__version__}         *")
    print("**                              **")
    print("***                            ***")
    print("****                          ****")
    print("**********************************")
    print("")


async def main():
    """Main async entry point."""
    print_header()

    args_parser = ArgumentsParser()
    args = args_parser.Parse()

    bot = PaymentBot(args.config)
    await bot.Run()


if __name__ == "__main__":
    asyncio.run(main())
