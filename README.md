# Telegram Payments Bot

| |
|---|
| [![PyPI - Version](https://img.shields.io/pypi/v/telegram_payment_bot.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/telegram_payment_bot/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram_payment_bot.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/telegram_payment_bot/) [![GitHub License](https://img.shields.io/github/license/ebellocchia/telegram_payment_bot?label=License)](https://github.com/ebellocchia/telegram_payment_bot?tab=MIT-1-ov-file) |
| [![Build](https://github.com/ebellocchia/telegram_payment_bot/actions/workflows/build.yml/badge.svg)](https://github.com/ebellocchia/telegram_payment_bot/actions/workflows/build.yml) [![Code Analysis](https://github.com/ebellocchia/telegram_payment_bot/actions/workflows/code-analysis.yml/badge.svg)](https://github.com/ebellocchia/telegram_payment_bot/actions/workflows/code-analysis.yml) |
| [![Codacy grade](https://img.shields.io/codacy/grade/c285797e0a8042f49202947924d1f2ac?label=Codacy%20Grade)](https://app.codacy.com/gh/ebellocchia/telegram_payment_bot/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) [![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/ebellocchia/telegram_payment_bot?label=CodeFactor%20Grade)](https://www.codefactor.io/repository/github/ebellocchia/telegram_payment_bot) |
| |

## Introduction

Telegram bot for handling payments in groups based on *pyrotgfork* (a maintained fork of the *pyrogram* library).

Payments can be either loaded from a *xls*/*xlsx* file or, better, from a Google Sheet. The advantages of the Google Sheet are:
- It can be easily shared with other people or admins.
- It can be automatically written by the service handling payments. For example: if users pay from a website, the website can automatically write the payments to the Google Sheet.

It is also possible to extend this to load payments data from other sources (e.g. a remote database) by inheriting and implementing the `PaymentsLoaderBase` class.\
Payments data can be either updated manually by the admins or, better, automatically (e.g. by the website where the payment is made). It depends on the infrastructure you have.

## Setup

### Create Telegram app

In order to use the bot, you need a Telegram bot token, an API ID, and an API hash.

To obtain them, create an app on the following website: [https://my.telegram.org/apps](https://my.telegram.org/apps).

### Installation

This package requires **Python >= 3.7**.


1. **Set up a virtual environment (optional but recommended)**:

```
python -m venv venv
source venv/bin/activate    # On Windows use: venv\Scripts\activate
```

2. **Install the bot:**

```
pip install telegram_payment_bot
```

**IMPORTANT NOTE:** This bot uses *pyrotgfork*. If you are not using a virtual environment, ensure that the standard *pyrogram* library (or forks) is not installed in your Python environment.
Since both libraries use the same package name, having both installed will cause conflicts and the bot will not function correctly.

3. **Set up the bot:**
Copy the **app** folder from the repository to your device. Edit the configuration file by specifying your API ID, API hash, bot token, and other parameters according to your needs (see the "Configuration" chapter).
4. **Run the bot:**
Inside the **app** folder, launch the **bot_start.py** script to start the bot:

```
python bot_start.py
```

---

#### Custom Configuration

When run without parameters, the bot uses **conf/config.ini** as the default configuration file. To specify a different configuration file, use:

```
python bot_start.py -c another_conf.ini
```

or:

```
python bot_start.py --config another_conf.ini
```

This allows you to manage different bots easily, each one with its own configuration file.

### Code analysis

To run code analysis:

```
mypy .
ruff check .
```

## Configuration

An example configuration file is provided in the **app/conf** folder.

The list of all configurable fields is shown below.

| Name | Description |
|---|---|
| **[pyrogram]** | *Configuration for Pyrogram* |
| `session_name` | Path of the file used to store the session. |
| `api_id` | API ID from [https://my.telegram.org/apps](https://my.telegram.org/apps). |
| `api_hash` | API hash from [https://my.telegram.org/apps](https://my.telegram.org/apps). |
| `bot_token` | Bot token from *BotFather*. |
| **[app]** | *Configuration for the app* |
| `app_is_test_mode` | Set to `true` to activate test mode, `false` otherwise. |
| `app_lang_file` | Path of custom language file in XML format (default: English). |
| **[users]** | *Configuration for users* |
| `authorized_users` | Comma-separated list of Telegram usernames authorized to use the bot |
| **[support]** | *Configuration for support* |
| `support_email` | Email address for support or sending payment receipts (default: empty). Only for showing to users when manually checking for payments. |
| `support_telegram` | Telegram username for support or sending payment receipts (default: empty). Only for showing to users when manually checking for payments. |
| **[payment]** | *Configuration for payments* |
| `payment_website` | Website for payments (default: empty). Only for showing to users when manually checking for payments. |
| `payment_check_on_join` | Check the payment status of new members as soon as they join the group (default: `true`) |
| `payment_check_dup_email` | Check for duplicated emails in payment data (default: `true`) |
| `payment_type` | Input source for payment data: `EXCEL_FILE` for xls/xlsx files, `GOOGLE_SHEET` for Google Sheets |
| `payment_excel_file` | Name of the Excel file for payment data (loaded only if `payment_type` is `EXCEL_FILE`) |
| `payment_google_sheet_id` | ID of the Google Sheet for payment data (loaded only if `payment_type` is `GOOGLE_SHEET`) |
| `payment_google_cred_type` | Credentials type: `OAUTH2` or `SERVICE_ACCOUNT` (default: `OAUTH2`, loaded only if `payment_type` is `GOOGLE_SHEET`) |
| `payment_google_cred` | Name of the *json* credentials file (default: `credentials.json`, loaded only if `payment_type` is `GOOGLE_SHEET`) |
| `payment_google_cred_path` | Path where the Google OAuth2 token file will be saved (loaded only if `payment_type` is `GOOGLE_SHEET` and `payment_google_cred_type` is `OAUTH2`) |
| `payment_use_user_id` | If `true`, `payment_user_col` is treated as a numerical User ID; otherwise, it is treated as a username |
| `payment_worksheet_idx` | Worksheet index (default: `0`) |
| `payment_email_col` | Column letter containing the payment email (default: `A`, maximum: `Z`) |
| `payment_user_col` | Column letter containing the user info (default: `B`, maximum: `Z`). Depends on the `payment_use_user_id` flag. |
| `payment_expiration_col` | Column letter containing the payment expiration date (default: `C`, maximum: `Z`) |
| `payment_date_format` | Date format used in payment data (default: `%d/%m/%Y`) |
| **[email]** | *Configuration for payment reminder emails* |
| `email_enabled` | Enable or disable emails (default: `false`). If `false`, the following fields are ignored. |
| `email_auth_type` | Email authentication type: `NONE`, `SSL_TLS`, or `STARTTLS` |
| `email_from` | Sender email address |
| `email_reply_to` | Reply-to email address |
| `email_host` | SMTP host for sending emails |
| `email_user` | Username for SMTP authentication |
| `email_password` | Password for SMTP authentication |
| `email_subject` | Subject line of the email |
| `email_alt_body` | Path to the file containing the plain text email body |
| `email_html_body` | Path to the file containing the HTML email body |
| **[logging]** | *Configuration for logging* |
| `log_level` | Log level, same as Python logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default: `INFO`. |
| `log_console_enabled` | Set to `true` to enable console logging, `false` otherwise (default: `true`) |
| `log_file_enabled` | Set to `true` to enable file logging, `false` otherwise (default: `false`). If `false`, the following fields are ignored. |
| `log_file_name` | Name of the log file |
| `log_file_use_rotating` | Set to `true` to use a rotating log file, `false` otherwise |
| `log_file_max_bytes` | Maximum size in bytes for a log file before rotating. Valid only if `log_file_use_rotating` is `true`. |
| `log_file_backup_cnt` | Maximum number of log files to keep. Valid only if `log_file_use_rotating` is `true`. |
| `log_file_append` | Set to `true` to append to the log file, `false` to overwrite it each time. Valid only if `log_file_use_rotating` is `false`. |

## Supported Commands

List of supported commands:
- `help`: show help message
- `alive`: show if bot is active
- `paybot_set_test_mode true/false`: enable/disable test mode
- `paybot_is_test_mode`: show if test mode is enabled
- `paybot_auth_users`: show the list of authorized users that can use the bot
- `paybot_chat_info`: show the chat information (can be run only in group)
- `paybot_users_list`: show the users list (can be run only in group)
- `paybot_invite_link`: generate a new invite link (can be run only in group)
- `paybot_version`: show the bot version
- `paybot_check_username [<HOURS_LEFT>]`: show the list of chat members without a username (can be run only in group)
    - `HOURS_LEFT` (optional): hours left to set the username before being removed (only for printing the message). Hours are automatically converted to days if greater than 47. If less than 1, it'll print "as soon as possible". Default value: 0.
- `paybot_remove_username`: remove all the chat members without a username (can be run only in group)
- `paybot_set_check_on_join true/false`: enable/disable payment check when a new member joins
- `paybot_is_check_on_join`: show if payment check when a new member joins is enabled
- `paybot_check_data`: check payments data for errors (e.g. invalid dates, duplicated users) and show them
- `paybot_email_payment [<DAYS_LEFT>]`: send a reminder email to chat members whose payment is expiring in the specified number of days
    - `DAYS_LEFT` (optional): number of days within which the payment expires. Less than 1 means expiring today. Default value: 0.
- `paybot_check_payment [<DAYS_LEFT>] [<LAST_DAY>]`: show the list of chat members whose payment is expiring in the specified number of days (can be run only in group)
    - `DAYS_LEFT` (optional): number of days within which the payment expires. Less than 1 means expiring today. Default value: 0.
    - `LAST_DAY` (optional): last day to complete the payment before being removed (only for printing the message). If less than 1 or greater than 31, it'll print "within few days". Default value: 0.
- `paybot_remove_payment`: remove the chat members whose payment has expired (can be run only in group)
- `paybot_task_start PERIOD_HOURS`: start payment check task with the specified period
    - `PERIOD_HOURS`: task period in hours
- `paybot_task_stop`: stop payment check task
- `paybot_task_info`: show payment check task information
- `paybot_task_add_chat`: add the current chat to the payment check task
- `paybot_task_remove_chat`: remove the current chat from the payment check task
- `paybot_task_remove_all_chats`: remove all chats from the payment check task

Add `quiet` or `q` as last parameter to send the bot response in a private chat instead of the group chat.

Users removed from the group are just kicked and not banned, so they can re-join later via invite links if necessary.\
When users are removed from the group (either because they had no username or they didn't pay), a new invite link is generated and sent to all authorized users in a private chat.\
This automatically revokes the old invite link and prevents those users from joining again using it.

When checking for payments, a user is removed from the group if:
- He has no Telegram username
- His Telegram username or user ID is not found in the payments data
- His payment is expired

If `payment_check_dup_email` is set to true:
- If multiple rows have the same email address, only the first row will be loaded and all the others will be skipped (therefore, those users won't be considered as valid payments)
- Rows with duplicated email address will be printed by the `paybot_check_data` command

## Payment Check Task

It's suggested to run a background task to check for payments periodically. It can be started/stopped with the `paybot_task_start`/`paybot_task_stop` commands.\
The task can check multiple groups at once (sharing the same payments data, of course). The groups can be added/removed with the `paybot_task_add_chat`/`paybot_task_remove_chat` commands (either while the task is running or stopped).\
If no group was added, the task will simply run without checking any group.

**Scheduling Logic:**
The task period starts from the specified hour (ensure the VPS time is correct):

- Period of 8h starting at 00:00: sends at 00:00, 08:00, 16:00
- Period of 6h starting at 10:00: sends at 10:00, 16:00, 22:00, 04:00

## Payment File

The payment file can be either an **xls**/**xlsx** file or a Google Sheet.

In the case of a Google Sheet, two types of authorization are possible:
- **OAuth2 flow:**
    - Create it in the [Google Cloud Console](https://console.cloud.google.com) (under *APIs & Services* → *Credentials*) and download the *json* file with the credentials.
    - Copy the *json* file into the **app/cred** folder. The filename must match the configured one (i.e., `payment_google_cred`).
    - The first time the bot loads the Sheet, the browser will automatically open and you will be asked to log in to your Google account to allow the bot to access the sheet. If the bot is running on a VPS, it will print the URL for you to open on your PC.
    - A *json* file will be automatically created in the configured folder (i.e., `payment_google_cred_path`).
    - This *json* file allows the bot to access the sheet in the future without asking for further authorization (it can also be moved to other devices).
- **Service account (recommended):**
    - Create it in the [Google Cloud Console](https://console.cloud.google.com) (under *APIs & Services* → *Credentials*) and download the *json* file with the credentials.
    - Copy the *json* file into the **app/cred** folder. The filename must match the configured one (i.e., `payment_google_cred`).
    - A service account is pre-authorized, so there is no need to authorize the bot via a browser. You simply need to share the Google Sheet with the service account's Gmail address.

Please refer to the official Google documentation for more details on how to create these credentials.

In both cases (Google Sheet or Excel file), the file must contain the following columns starting from the second row (the first row is used as a header):
- Email address used for payment (for convenience, as an email is usually required by payment platforms)
- Telegram user ID or username
- Expiration date of the payment, in the format specified by `payment_date_format`

The indexes for these columns are set in the configuration file. You can add other columns if necessary: they will be ignored by the bot.

## Channel Limitations

When used in channels:
- The bot can check for payments periodically but it cannot check users immediately when they join
- All admins can use the bot, not only authorized users
- Commands in quiet mode will send the result to authorized users instead of privately to the user that executed the command
- Due to a Telegram limitation, only 200 members can be managed

## Run the Bot

The bot must be a group administrator in order to remove non-paying members.

It is recommended to run the bot 24/7 on a VPS.

### Docker

Docker files are also provided, to run the bot in a Docker container.
In this case, the configuration file can be set by setting the `CONFIG_FILE` variable, for example:

```
CONFIG_FILE=conf/config.ini docker compose up -d --build
```

**NOTE:** Adjust the `TZ=Europe/Rome` variable in `docker-compose.yml` to match your timezone.

## Test Mode

Test mode can be used to test the bot's functionality without affecting the group members. When active:
- Users are not kicked from the group even if they lack a username or have not paid (this applies to manual commands, new members joining, and periodic checks).
- Emails are not sent to users who have not yet paid.

Moreover, the payment task period will be applied in **minutes** instead of hours. This allows you to quickly verify that the bot is working as expected.

## Translation

Bot messages can be translated using a custom XML file specified in the `app_lang_file` field. An Italian example is provided in **app/lang**.

# License

This software is available under the MIT license.
