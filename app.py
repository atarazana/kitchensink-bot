import os
import logging
import signal

from threading import Thread

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners

from db import init_db

from rest import rest


def sigterm_handler(signum, frame):
    print("Received SIGTERM. Shutting down gracefully...")
    # You can perform cleanup or additional shutdown tasks here if needed.
    os._exit(0)  # Exit the application


signal.signal(signal.SIGTERM, sigterm_handler)

# Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", logging.INFO)
BOLT_SDK_LOGGING_LEVEL = os.environ.get("BOLT_SDK_LOGGING_LEVEL", logging.INFO)

logging.basicConfig(level=LOGGING_LEVEL)

# Create a custom logger for slack_sdk.webhook.client
webhook_logger = logging.getLogger("slack_sdk.webhook.client")
webhook_logger.setLevel(BOLT_SDK_LOGGING_LEVEL)  # Set the desired logging level here

# Register Listeners
register_listeners(app)

# Start Bolt app
if __name__ == "__main__":
    init_db()

    # Run the Flask app from the subfolder on a separate thread
    flask_thread = Thread(target=lambda: rest.run(debug=False, host="0.0.0.0", port=5000))
    flask_thread.start()

    try:
        # Your application logic can go here.
        SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()

        # Wait for the thread to finish (this will not block Ctrl+C)
        flask_thread.join()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully (SIGINT)
        print("Received KeyboardInterrupt (Ctrl+C). Shutting down...")
        os._exit(0)  # Exit the application
