import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_file='message_queue.db'):
        """Initialize database connection and create tables if they don't exist"""
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        """Create the necessary tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Create messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS queued_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER,
                        chat_id INTEGER,
                        message_text TEXT,
                        media_path TEXT,
                        created_at TIMESTAMP,
                        retries INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'pending',
                        error_message TEXT,
                        is_edit BOOLEAN DEFAULT 0
                    )
                ''')
                
                # Add is_edit column if it doesn't exist
                try:
                    cursor.execute('ALTER TABLE queued_messages ADD COLUMN is_edit BOOLEAN DEFAULT 0')
                except sqlite3.OperationalError:
                    # Column already exists
                    pass
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def queue_message(self, message_id, chat_id, message_text=None, media_path=None, is_edit=False):
        """Add a message to the queue"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO queued_messages 
                    (message_id, chat_id, message_text, media_path, created_at, is_edit)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (message_id, chat_id, message_text, media_path, datetime.now(), is_edit))
                conn.commit()
                logger.info(f"Message {message_id} queued successfully")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error queuing message: {str(e)}")
            raise

    def get_pending_messages(self, limit=10):
        """Get pending messages that need to be forwarded"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM queued_messages 
                    WHERE status = 'pending' 
                    AND retries < 3
                    ORDER BY created_at ASC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting pending messages: {str(e)}")
            return []

    def update_message_status(self, message_id, status, error_message=None):
        """Update the status of a message in the queue"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                if status == 'failed':
                    cursor.execute('''
                        UPDATE queued_messages 
                        SET status = ?, error_message = ?, retries = retries + 1
                        WHERE message_id = ?
                    ''', (status, error_message, message_id))
                else:
                    cursor.execute('''
                        UPDATE queued_messages 
                        SET status = ?
                        WHERE message_id = ?
                    ''', (status, message_id))
                conn.commit()
                logger.info(f"Message {message_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")
            raise

    def cleanup_old_messages(self, days=7):
        """Clean up old messages from the queue"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM queued_messages 
                    WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
                    AND status != 'pending'
                ''', (str(days),))
                conn.commit()
                logger.info(f"Cleaned up messages older than {days} days")
        except Exception as e:
            logger.error(f"Error cleaning up old messages: {str(e)}")
            raise 