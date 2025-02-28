# Deploying Telegram Message Forwarder to Render with Docker

This guide explains how to deploy the Telegram Message Forwarder project to Render using Docker.

## Prerequisites

1. A [Render](https://render.com) account
2. Your Telegram API credentials:
   - API ID
   - API Hash
   - Session String
3. Source and destination channel information

## Deployment Steps

### Option 1: Deploy via Git Repository

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Log in to your Render account
3. Click on "New" and select "Web Service"
4. Connect your Git repository
5. Select "Docker" as the environment
6. Configure the following environment variables in the Render dashboard:
   - `TELEGRAM_API_ID`: Your Telegram API ID
   - `TELEGRAM_API_HASH`: Your Telegram API Hash
   - `SOURCE`: Your source channel (e.g., @channelname)
   - `DESTINATION_CHANNEL`: Your destination channel
   - `TELEGRAM_SESSION_STRING`: Your Telegram session string
7. Click "Create Web Service"

### Option 2: Deploy via Render YAML

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Log in to your Render account
3. Click on "New" and select "Blueprint"
4. Connect your Git repository
5. Render will detect the `render.yaml` file and configure the service accordingly
6. Add your environment variables through the Render dashboard
7. Click "Apply"

## Generating Session String

If you need to generate a new session string:

1. Run the `generate_session.py` script locally:
   ```
   python generate_session.py
   ```
2. The script will prompt you to enter your phone number and the verification code
3. Save the generated session string as the `TELEGRAM_SESSION_STRING` environment variable in Render

## Testing Your Deployment

1. Once deployed, visit your service URL (e.g., https://telegram-forwarder.onrender.com)
2. The service should show as "active" if running correctly
3. You can visit `/start` to start the bot if it's not running
4. Check the health status at `/health`

## Troubleshooting

If you encounter issues:

1. Check the Render logs for error messages
2. Verify that all environment variables are set correctly
3. Ensure your Telegram session is valid
4. Make sure you have joined both the source and destination channels with your Telegram account

## Local Docker Testing

To test the Docker setup locally before deployment:

```bash
# Build and run using docker-compose
docker-compose up --build
```

This will start the service locally at http://localhost:8080
