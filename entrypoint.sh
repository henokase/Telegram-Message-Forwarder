#!/bin/bash
set -e

# Print environment information for debugging
echo "Starting Telegram Forwarder with the following configuration:"
echo "PORT: $PORT"
echo "RENDER: $RENDER"
echo "TELEGRAM_API_ID is set: $(if [ -n "$TELEGRAM_API_ID" ]; then echo "YES"; else echo "NO"; fi)"
echo "TELEGRAM_API_HASH is set: $(if [ -n "$TELEGRAM_API_HASH" ]; then echo "YES"; else echo "NO"; fi)"
echo "SOURCE is set: $(if [ -n "$SOURCE" ]; then echo "YES"; else echo "NO"; fi)"
echo "DESTINATION_CHANNEL is set: $(if [ -n "$DESTINATION_CHANNEL" ]; then echo "YES"; else echo "NO"; fi)"
echo "TELEGRAM_SESSION_STRING is set: $(if [ -n "$TELEGRAM_SESSION_STRING" ]; then echo "YES"; else echo "NO"; fi)"

# Start the web service
echo "Starting Gunicorn server..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --log-file - --log-level debug