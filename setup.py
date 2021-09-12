import setuptools
import re

VERSION_FILE = "telegram_payment_bot/_version.py"

with open("README.md", "r") as f:
    long_description = f.read()

def load_version():
    version_line = open(VERSION_FILE).read().rstrip()
    vre = re.compile(r'__version__: str = "([^"]+)"')
    matches = vre.findall(version_line)

    if matches and len(matches) > 0:
        return matches[0]
    else:
        raise RuntimeError("Cannot find version string in %s" % VERSION_FILE)

version = load_version()

setuptools.setup(
    name="telegram_payment_bot",
    version=version,
    author="Emanuele Bellocchia",
    author_email="ebellocchia@gmail.com",
    maintainer="Emanuele Bellocchia",
    maintainer_email="ebellocchia@gmail.com",
    description="Telegram bot for handling payments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    install_requires = ["google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib", "pyrogram", "tgcrypto", "xlrd", "apscheduler"],
    packages=setuptools.find_packages(exclude=[]),
    package_data={"telegram_payment_bot": ["lang/lang_en.xml"]},
    keywords="telegram, bot, telegram bot, payments, payments check",
    platforms = ["any"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
)
