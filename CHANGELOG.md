# 0.6.2

- Migrate Google OAuth flow after deprecation

# 0.6.1

- Fix some _mypy_ and _prospector_ warnings
- Add configuration for _isort_ and run it on project

# 0.6.0

- Add support for _pyrogram_ version 2 (version 1 still supported)

# 0.5.3

- Members without username or that haven't paid are kicked until no one left (useful in channels with more than 200 members)

# 0.5.2

- Fix usage in channels
- Fix ban method name for _pyrogram_ 1.4

# 0.5.1

- Add command for showing bot version

# 0.5.0

- Add possibility to disable duplicated email check
- Project re-organized into folders

# 0.4.0

- Add the possibility to use either user ID or username in payment file
- Bot works also in channels in addition to supergroups
- Fix group only restriction to `/paybot_task_remove_all_chats` command
- Add single handlers for message updates, to avoid being notified of each single message sent in groups

# 0.3.7

- Fix bug when checking the correctness or payments data

# 0.3.6

- Rename commands by adding the `paybot_` prefix, to avoid conflicts with other bots
- Email is checked for duplication in payment file

# 0.3.5

- Use _pygsheets_ library for reading Google Sheets
- File columns specified using the letter instead of the index

# 0.3.4

- Add configuration files for _flake8_ and _prospector_
- Fix all _flake8_ warnings
- Fix the vast majority of _prospector_ warnings
- Remove all star imports (`import *`)

# 0.3.3

- Fix wrong imports
- Add typing to class members
- Fix _mypy_ errors

# 0.3.2

- Minor bug fixes

# 0.3.1

- Fix sentences sent during periodic payment check
- Fix some sentence names
- Exclude bots and self from username/payment check

# 0.3.0

- Payment check task is not statically configured anymore, but now it can be configured dynamically with specific commands
- Payment check on member join can be configured dynamically with specific commands
- Possibility to usa a "normal" log file handler in addition to the rotating file handler
- Add placeholders to translation sentences (in this way, they can be moved to different positions depending on the language)

# 0.2.0

- Add possibility to translate bot messages in different languages using a custom xml file (`app_lang_file`)
- Add possibility to leave some configuration fields  empty (`support_email`, `support_telegram`, `payment_website`)
- Add possibility to check and change test mode without restarting the bot using commands `set_test_mode` and `is_test_mode`
- Add possibility to check payments data using command `check_payments_data`
- Add possibility to set the date format for payments data (`payment_date_format`)
- Add possibility to disable emails (`email_enabled`) and payment check when members join (`payment_check_on_join`)
- Payments data is checked for duplicated usernames and invalid dates
- Change periodical payment check period from seconds to minutes (`payment_check_period_sec` to `payment_check_period_min`)

# 0.1.0

First release
