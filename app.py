from flask import Flask, render_template, jsonify
import threading
import telegram_forwarder
import logging
import os
import sys

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Log to stdout for Render
)
logger = logging.getLogger(__name__)

# Global variable to store bot status
bot_status = {
    "running": False,
    "last_message": None,
    "error": None,
    "start_time": None
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
    try:
        return jsonify({
            "status": "active" if bot_status["running"] else "inactive",
            "error": bot_status["error"],
            "last_message": bot_status["last_message"],
            "service": "Telegram Forwarder",
            "health": "ok"
        })
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        if bot_status["running"] and not bot_status["error"]:
            return jsonify({"status": "healthy"}), 200
        return jsonify({
            "status": "unhealthy",
            "error": bot_status["error"]
        }), 503
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/start')
def start():
    """Start the bot if it's not running"""
    try:
        if not bot_status["running"]:
            thread = threading.Thread(target=run_bot)
            thread.daemon = True
            thread.start()
            return jsonify({"status": "started"}), 200
        return jsonify({"status": "already running"}), 200
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({"error": str(e)}), 500

def start_server():
    """Start the Flask server with the correct port"""
    try:
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Get port from environment variable (Render sets this)
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_server() 