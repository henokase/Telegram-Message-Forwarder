# Telegram Message Forwarder

A Python script that monitors a specified Telegram group or channel and automatically forwards messages (including media) to a destination channel.

## Features

-   Monitors source group/channel for new messages
-   Forwards both text and media messages
-   Preserves sender information for group messages
-   Supports all message types (text, photos, videos, documents, etc.)
-   Comprehensive error handling and logging
-   Uses user account authentication for access without admin privileges
-   Offline mode with message queuing
-   Automatic retry mechanism for failed forwards

## Prerequisites

-   Python 3.x
-   Telegram API credentials (API ID and Hash) from https://my.telegram.org/apps

## Installation

1. Clone this repository
2. Create and activate virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Unix/MacOS:
    source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2. Edit `.env` and fill in your:
    - Telegram API credentials (API_ID and API_HASH)
    - Source group/channel identifier:
        - For public groups/channels: use the username (e.g., @groupname)
        - For private groups/channels: use the ID (e.g., -100xxxxxxxxxx)
    - Destination channel ID

### Finding Group/Channel IDs

To get a group or channel ID:

1. Forward a message from the group/channel to @userinfobot
2. The bot will reply with information including the ID
3. For private groups/channels, the ID will be in the format -100xxxxxxxxxx

## Usage

Run the script:

```bash
python telegram_forwarder.py
```

The script will:

1. Connect to Telegram using your credentials
2. Monitor the source group/channel for new messages
3. Forward messages to the destination channel:
    - For group messages: includes sender information
    - For channel messages: forwards as is
4. Log all activities to both console and `telegram_forwarder.log`

## Message Formatting

### Group Messages

Messages from groups are formatted to include sender information:

```
From: John Doe (@username)

[Original message text]
```

### Channel Messages

Messages from channels are forwarded as is, maintaining the original format.

## Logging

The script logs all activities to:

-   Console (stdout)
-   `telegram_forwarder.log` file

Log levels:

-   INFO: Normal operations (connection, message forwarding)
-   ERROR: Issues that need attention (connection problems, forwarding failures)

## Error Handling

The script includes comprehensive error handling for:

-   Missing configuration
-   Connection issues
-   Message forwarding failures
-   Media download/upload errors

## Security Notes

-   Keep your API credentials secure
-   Never commit the `.env` file to version control
-   Use a dedicated user account for the script

## License

MIT License
