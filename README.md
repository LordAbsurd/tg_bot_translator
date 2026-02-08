# tg bot translator

Telegram bot for text translation in private chats, groups, and inline mode.
You can check it in Telegram @transmebot

## Features

- Inline translation: `@your_bot EN text`
- Translation without explicit language code (uses user default language)
- User language preference stored in MySQL
- Long polling mode out of the box
- WSGI `application` entrypoint for webhook deployment

## Project files

- `main.py` - bot handlers, Telegram API calls, long polling, WSGI webhook handler
- `mysql_db_functions.py` - DB access and table initialization
- `config.py` - available language codes and language names
- `requirements.txt` - Python dependencies
- `.env.example` - example environment variables

## Requirements

- Python 3.10+
- MySQL 8+ (or compatible)
- Telegram bot token from BotFather

## Configuration

1. Copy `.env.example` to `.env`.
2. Fill in real values:

```env
TG_TOKEN=your_real_bot_token
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=test
MYSQL_USER=bot
MYSQL_PASSWORD=your_password
MYSQL_AUTH_PLUGIN=mysql_native_password
```

## Install

```bash
pip install -r requirements.txt
```

## Run (long polling)

```bash
python main.py
```

On startup, the bot checks token validity and creates required DB tables if they do not exist.

## Webhook deployment

The WSGI entrypoint is exposed as:

```python
application = webhook_handler
```

Expected webhook path is `/webhook`.

## Security notes

- Do not commit `.env`.
- Rotate your Telegram token if it was ever exposed in git history.
- Avoid committing logs containing user messages or IDs.

## License

This project is licensed under the MIT License. See `LICENSE`.
