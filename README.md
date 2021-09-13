# Telegram Payments Bot

Telegram bot for handling payments in groups based on *pyrogram* library.\
Payments data can be loaded either from an *xls*/*xlsx* file or from a Google Sheet (in this way, it can be shared with other admins).\
It is also possible to extend this to load payments data from other sources (e.g. a remote database) by inheriting and implementing the *PaymentsLoaderBase* class, but I didn't need to do it so far.\
Payments data can be updated either manually by the admins or, better, automatically (e.g. by the website where the payment is made, via a webhook). It depends on the infrastructure you have.

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
- **/set_test_mode [true/false]**: enable/disable test mode
- **/is_test_mode**: show if test mode is enabled
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
This automatically revokes the old invite link and prevents those users to join again using it.

When checking for payments, a user is removed by group if:
- He has no Telegram username
- His Telegram username is not found in the payments data
- His payment is expired

## Periodical Checks

In addition to the commands, it's possible to run periodical checks.\
These checks are:
- Remove a user that hasn't paid as soon as he joins the group
- Remove users that hasn't paid periodically

Both checks can be disabled if needed using the *payment_check_on_join* and *payment_check_period_min* fields.

## Run the Bot

If you just need to run bot once in a while (e.g. once a week), you can do it manually using the *check_no_payment* and *remove_no_payment* commands. In this case, it's sufficient to run the bot locally on the PC when needed.\
If you prefer to let the bot run automatically and check for payment periodically, it'll be better to run it 24h/24h on a VPS.

## Payment File

The payment file can be either a *xls*/*xlsx* file (*xlrd* library is used) or a Google Sheet.\
In case a Google Sheet is used:
1. Create a project on [Google Cloud Console](https://console.cloud.google.com)
2. Go to *APIs & Services*, then *Credentials* and select *Configure Consent Screen*
3. Create a new app and publish it, it doesn't need to be verified (but you can verify it, of course)
4. Go back to the *Credentials* page and create the credentials for OAuth client ID by selecting *Create Credentials*
5. Select *Desktop app*, choose a name and download the *json* file with the credentials
6. Go to the *Library* page, search for Google Sheet and enable Google Sheet APIs
7. Rename the *json* file to the name specified in the configuration file (*payment_google_cred*) and place it in the *app* folder
8. The first time the bot loads your Google Sheet, you'll be asked to login into your Google account and allow the bot to access the sheet. After this, a *pickle* file with the name you configured (*payment_google_pickle*) will be automatically created.
9. This *pickle* file allows the bot to access the sheet next times, so you don't need to allow it again
10. If you move the bot to another PC or server, just keep the *json* and *pickle* files to grant the bot access to the sheet without repeating the whole procedure

For more information: [create project](https://developers.google.com/workspace/guides/create-project), [create credentials](https://developers.google.com/workspace/guides/create-credentials)

In both cases (Google Sheet or Excel file), the file shall contain the following columns starting from the second row (the first row is used as header):
- Email address used for paying (for convenience, since an email address is usually required in payment platforms)
- Telegram username
- Expiration date of the payment in the format dd/mm/yyyy or yyyy-mm-dd

The indexes of these columns are set in the configuration file. It is possible to add other columns beside these if necessary, they are simply ignored by the bot.

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
