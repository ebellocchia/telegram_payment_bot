# Telegram Payments Bot

Telegram bot for handling payments in groups based on *pyrogram* library.\
The payment can be loaded either from an *xls*/*xlsx* file or from a Google Sheet (in this way, it can be shared with other admins).\
It is possible to extend this in order to load payment data from other sources (e.g. a remote database) by inheriting and implementing the *PaymentsLoaderBase* class, but I didn't need to do it.

## Setup

### Create Telegram app

In order to use the bot, in addition to the bot token you also need an APP ID and hash.\
To get them, create an app using the following website: [https://my.telegram.org/apps](https://my.telegram.org/apps).

### Installation

Just run pip in this folder as follows:

    python setup.py install

To run the bot, move to the *app* folder and run the *bot.py* script:

    cd app
    python bot.py

When run with no parameter, *conf/config.ini* will be the default configuration file (in this way it can be used for different groups).\
To specify a different configuration file:

    python bot.py -c another_conf.ini
    python bot.py --config another_conf.ini

## Configuration

An example of configuration file is provided in the *app/conf* folder.\
The list of all possible fields that can be set is shown below.

|Name|Description|
|---|---|
|**[pyrogram]**|Configuration for pyrogram|
|session_name|Session name of your choice|
|api_id|API ID from [https://my.telegram.org/apps](https://my.telegram.org/apps)|
|api_hash|API hash from [https://my.telegram.org/apps](https://my.telegram.org/apps)|
|bot_token|Bot token from BotFather|
|**[app]**|Configuration for app|
|app_is_test_mode|True to activate test modem false otherwise|
|app_lang_file|Language file in XML format (default: English)|
|**[users]**|Configuration for users|
|authorized_users|List of Telegram usernames that are authorized to use the bot, comma separated|
|**[support]**|Configuration for support|
|support_email|Email for getting support or send payments receipts (can be left emtpy if none)|
|support_telegram|Telegram username for getting support or send payments receipts (can be left emtpy if none)|
|**[payment]**|Configuration for payment|
|payment_website|Website for payment (can be left emtpy if none)|
|payment_check_on_join|Flag to check the payment of new members as soon as they join the group|
|payment_check_period_min|Period in minutes for periodical check. 1 is the minimum value (any value less than 1 will disable the periodical check).|
|payment_check_chat_ids|IDs of groups to be periodical checked, comma separated (can be left empty). This assumes that all groups are linked to the same payments.|
|payment_type|Input for payment data: *EXCEL_FILE* for using xls/xlsx file, *GOOGLE_SHEET* for using a Google Sheet|
|payment_excel_file|Name of the Excel file used for payment data, valid only if *payment_type* is *EXCEL_FILE*|
|payment_google_sheet_id|ID of the Google Sheet used for payment data, valid only if *payment_type* is *GOOGLE_SHEET*|
|payment_google_cred|Name of the *json* file for the OAuth credentials (default: *credentials.json*), valid only if *payment_type* is *GOOGLE_SHEET*|
|payment_google_pickle|Name of pickle file used for Google login (default: *token.pickle*), valid only if *payment_type* is *GOOGLE_SHEET*|
|payment_email_col|Index of the table column containing the email used for paying (default: 0)|
|payment_username_col|Index of the table column containing the username (default: 1)|
|payment_expiration_col|Index of the table column containing the payment expiration date (default: 2)|
|**[email]**|Configuration for email that reminds users to pay|
|email_enabled|Email enable flag. If False, all the next fields can be skipped.|
|email_from|Email sender|
|email_reply_to|Email reply-to|
|email_host|Host for sending email|
|email_user|Username for logging to host|
|email_password|Password for logging to host|
|email_subject|Email subject|
|email_alt_body|File containing email alternate body (text)|
|email_html_body|File containing email HTML body|
|**[logging]**|Configuration for logging|
|log_level|Log level, same of python logging (*DEBUG*, *INFO*, *WARNING*, *ERROR*, *CRITICAL*)|
|log_console_enabled|True to enable logging to console, False otherwise|
|log_file_enabled|True to enable logging to file, False otherwise|
|log_file_name|Log file name|
|log_file_append|True to append to log file, False to start from a new file each time|
|log_file_max_bytes|Maximum size in bytes for a log file. When reached, a new log file is created up to *log_file_backup_cnt*.|
|log_file_backup_cnt|Maximum number of log files|

## Supported Commands

List of supported commands:
- **/help**: show help message
- **/alive**: show if bot is active
- **/auth_users**: show the list of authorized users that can use the bot
- **/chat_info**: show the chat information (can be run only in group)
- **/users_list**: show the users list (can be run only in group)
- **/invite_link**: generate a new invite link (can be run only in group)
- **/check_no_username [<HOURS_LEFT>]**: show the list of chat members without a username (can be run only in group)
    - *HOURS_LEFT*: hours left to set the username before being removed (only for printing the message). Hours are automatically converted to days if greater than 47. If zero, it'll print "as soon as possible".
- **/remove_no_username**: remove all the chat members without a username (can be run only in group)
- **/email_no_payment [<DAYS_LEFT>]**: send a reminder email to chat members whose payment is expiring in the specified number of days
    - *DAYS_LEFT*: number of days within which the payment expires. Zero means expiring today.
- **/check_no_payment [<DAYS_LEFT>] [<LAST_DAY>]**: show the list of chat members whose payment is expiring in the specified number of days (can be run only in group)
    - *DAYS_LEFT*: number of days within which the payment expires. Zero means expiring today.
    - *LAST_DAY*: last day to complete the payment before being removed (only for printing the message). If zero, it'll print "within few days".
- **/remove_no_payment**: remove the chat members whose payment has expired (can be run only in group)

Add *quiet* or *q* as last parameter to send the bot response in a private chat instead of the group chat.

Users removed from the group are just kicked and not banned, so they can re-join later via invite links if necessary.\
When users are removed from the group (either because they had no username or they didn't pay), a new invite link is generated and sent to all authorized users in a private chat.\
This automatically revokes the old invite link and prevents those users to join again.

## Periodical Checks

In addition to the commands, it's possible to run periodical checks.\
These checks are:
- Remove a user that hasn't paid as soon as he joins the group.
- Remove users that hasn't paid periodically

## Payment File

The payment file can be either a *xls*/*xlsx* file (*xlrd* library is used to read it) or a Google Sheet.\
In case a Google Sheet is used:
1. You should create a project for the bot on Google Cloud Console, create the credentials and download the *json* file for OAuth 2.0 client ID. For more information: [create project](https://developers.google.com/workspace/guides/create-project), [create credentials](https://developers.google.com/workspace/guides/create-credentials)
2. Rename the *json* file to the name specified in the configuration file and place it in the *app* folder
2. The first time you'll load the Google Sheet, you'll be asked to login into your Google account and allow the bot to access the sheet. After this, a *pickle* file will be automatically created.
3. This *pickle* files allows the bot to access the sheet next times, without the need to allow it
4. If you move the bot to another device, just keep the *json* and *pickle* files to grant the bot access to the sheet without repeating the whole procedure

In both cases, starting from the second row (the first row is used as header), the file shall contain the following columns:
- Email address used for paying (for convenience, since an email address is usually required in payment platforms)
- Telegram username
- Expiration date of the payment in the format dd/mm/yyyy or yyyy-mm-dd

The indexes of these columns are set in the configuration file. It is possible to add other columns beside these if necessary, they are simply ignored by the bot.

When checking for payments, a user is removed by group if:
- He has no Telegram username
- His Telegram username is not found in the payment file
- His payment is expired

## Test Mode

Test mode can be used to test the bot without any effect to the users of the group. When active:
- Users are not kicked from the group if they don't have a username or don't have paid, both when running a command and during periodical checks
- Emails are not sent to the users that hasn't paid yet

## Translation

The messages sent by the bot on Telegram can be translated into different languages (the default language is English) by providing a custom XML file.\
The XML file path is specified in the configuration file (*app_lang_file* field).\
An example XML file in italian is provided in the folder *app/lang*.

# License

This software is available under the MIT license.
