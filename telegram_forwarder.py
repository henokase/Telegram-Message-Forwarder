import os
import logging
import asyncio
from telethon import TelegramClient, events, types
from telethon.errors import FloodWaitError
from dotenv import load_dotenv
from database import Database
import aiohttp
import backoff

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_forwarder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SOURCE = os.getenv('SOURCE')
DESTINATION_CHANNEL = os.getenv('DESTINATION_CHANNEL')

client = TelegramClient('forwarder_session', API_ID, API_HASH)
db = Database()

def validate_channel_id(channel_id):
    """Validate and format channel ID"""
    if isinstance(channel_id, str):
        # If it's a username starting with @, return as is
        if channel_id.startswith('@'):
            return channel_id
        
        if channel_id.startswith('-100'):
            channel_id = channel_id[4:]
        
        try:
            channel_id = int(channel_id)
        except ValueError:
            return channel_id
    
    if isinstance(channel_id, int):
        return channel_id
    
    return channel_id

async def check_internet_connection():
    """Check if we have internet connection"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://1.1.1.1', timeout=5) as response:
                return response.status == 200
    except:
        return False

async def handle_media(message):
    """
    Handle media files in messages
    Returns the path to downloaded media file or None if no media
    """
    if not message.media:
        return None
    
    try:
        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file = os.path.join(temp_dir, f'media_{message.id}')
        await message.download_media(temp_file)
        logger.info(f"Media downloaded successfully: {temp_file}")
        return temp_file
    
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        return None

async def cleanup_media(file_path):
    """Clean up downloaded media files"""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Cleaned up media file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up media file: {str(e)}")

def get_message_type(message):
    """Determine the type of message for better handling"""
    if message.media:
        if isinstance(message.media, types.MessageMediaPhoto):
            return "photo"
        elif isinstance(message.media, types.MessageMediaDocument):
            return "document"
        elif isinstance(message.media, types.MessageMediaVideo):
            return "video"
        elif isinstance(message.media, types.MessageMediaAudio):
            return "audio"
        elif isinstance(message.media, types.MessageMediaVoice):
            return "voice"
        else:
            return "other_media"
    return "text"

def format_group_message(message):
    """Format group message to include sender information"""
    sender = message.sender
    if sender:
        sender_name = getattr(sender, 'first_name', '') or ''
        if getattr(sender, 'last_name', ''):
            sender_name += f" {sender.last_name}"
        if getattr(sender, 'username', ''):
            sender_name += f" (@{sender.username})"
    else:
        sender_name = "Unknown Sender"

    formatted_text = f"From: {sender_name}\n"
    if message.text:
        formatted_text += f"\n{message.text}"
    
    return formatted_text

@backoff.on_exception(backoff.expo, FloodWaitError, max_tries=5)
async def forward_message_with_retry(message, media_path=None):
    """Forward a message with exponential backoff retry"""
    try:
        msg_type = get_message_type(message)
        
        # For group messages, we want to include sender information
        is_group = isinstance(message.peer_id, types.PeerChat) or isinstance(message.peer_id, types.PeerChannel)
        formatted_text = format_group_message(message) if is_group else message.text

        dest_channel = validate_channel_id(DESTINATION_CHANNEL)
        
        try:
            entity = await client.get_entity(dest_channel)
            
            if media_path:
                await client.send_file(
                    entity=entity,
                    file=media_path,
                    caption=formatted_text
                )
            else:
                await client.send_message(
                    entity=entity,
                    message=formatted_text
                )
            return True
        except ValueError as e:
            logger.error(f"Invalid channel ID or username: {dest_channel}")
            raise
        except Exception as e:
            logger.error(f"Error sending message to channel: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error in forward_message_with_retry: {str(e)}")
        raise

@client.on(events.NewMessage(chats=SOURCE))
async def handle_new_message(event):
    """Handle new messages from source group/channel"""
    try:
        message = event.message
        logger.info(f"New message received from source")
        
        if not await check_internet_connection():
            logger.warning("No internet connection. Queuing message for later.")
            db.queue_message(
                message_id=message.id,
                chat_id=message.chat_id,
                message_text=message.text,
                media_path=None
            )
            return

        media_path = await handle_media(message)
        
        try:
            await forward_message_with_retry(message, media_path)
            logger.info("Message forwarded successfully")
        except Exception as e:
            logger.error(f"Failed to forward message: {str(e)}")

            db.queue_message(
                message_id=message.id,
                chat_id=message.chat_id,
                message_text=message.text,
                media_path=media_path
            )
        finally:
            if media_path:
                await cleanup_media(media_path)
    except Exception as e:
        logger.error(f"Error in handle_new_message: {str(e)}")

async def process_message_queue():
    """Process queued messages"""
    while True:
        try:
            if not await check_internet_connection():
                logger.warning("No internet connection. Waiting before processing queue...")
                await asyncio.sleep(60)
                continue

            pending_messages = db.get_pending_messages(limit=10)
            
            for msg in pending_messages:
                try:
                    message_id, chat_id, message_text, media_path = msg[1:5]
                    
                    # If there's media, we need to re-download it
                    new_media_path = None
                    if media_path:
                        # Here you would re-download the media
                        # For now, we'll just use text
                        pass

                    message = await client.get_messages(chat_id, ids=message_id)
                    
                    if message:
                        await forward_message_with_retry(message, new_media_path)
                        db.update_message_status(message_id, 'completed')
                        logger.info(f"Successfully processed queued message {message_id}")
                    else:
                        db.update_message_status(message_id, 'failed', 'Message not found')
                        
                except Exception as e:
                    logger.error(f"Error processing queued message {message_id}: {str(e)}")
                    db.update_message_status(message_id, 'failed', str(e))
                finally:
                    if 'new_media_path' in locals() and new_media_path:
                        await cleanup_media(new_media_path)
            
            db.cleanup_old_messages(days=1)
            
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in queue processor: {str(e)}")
            await asyncio.sleep(60)

async def main():
    """Main function to run the client"""
    try:
        logger.info("Starting Telegram Forwarder...")
        
        if not all([API_ID, API_HASH, SOURCE, DESTINATION_CHANNEL]):
            raise ValueError("Missing required environment variables")
        
        dest_channel = validate_channel_id(DESTINATION_CHANNEL)
        logger.info(f"Using destination channel: {dest_channel}")
        
        await client.start()
        logger.info("Client started successfully")
        
        try:
            entity = await client.get_entity(dest_channel)
            logger.info(f"Successfully connected to destination channel: {entity.title if hasattr(entity, 'title') else dest_channel}")
        except Exception as e:
            logger.error(f"Failed to access destination channel: {str(e)}")
            raise
        
        os.makedirs('temp', exist_ok=True)
        
        asyncio.create_task(process_message_queue())
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise
    finally:
        try:
            import shutil
            if os.path.exists('temp'):
                shutil.rmtree('temp')
                logger.info("Cleaned up temp directory")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}") 