from flask import Flask, render_template
import threading
import telegram_forwarder
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variable to store bot status
bot_status = {
    "running": False,
    "last_message": None,
    "error": None
}

def run_bot():
    """Run the Telegram forwarder bot in a separate thread"""
    try:
        bot_status["running"] = True
        bot_status["error"] = None
        telegram_forwarder.start_bot()
    except Exception as e:
        bot_status["error"] = str(e)
        logger.error(f"Bot error: {e}")
    finally:
        bot_status["running"] = False

@app.route('/')
def home():
    """Home page showing bot status"""
    return {
        "status": "active" if bot_status["running"] else "inactive",
        "error": bot_status["error"],
        "last_message": bot_status["last_message"]
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    if bot_status["running"] and not bot_status["error"]:
        return {"status": "healthy"}, 200
    return {"status": "unhealthy", "error": bot_status["error"]}, 503

@app.route('/start')
def start():
    """Start the bot if it's not running"""
    if not bot_status["running"]:
        thread = threading.Thread(target=run_bot)
        thread.daemon = True
        thread.start()
        return {"status": "started"}, 200
    return {"status": "already running"}, 200

if __name__ == '__main__':
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 