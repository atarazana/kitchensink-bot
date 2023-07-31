import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners

from db import init_db

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

# @app.event("app_mention")
# def handle_app_mention(body, say, event):
#     message = event["text"]
#     user = event["user"]
#     channel = event["channel"]
#     response = f"Hi <@{user}>! You mentioned me with the message: {message}"
#     say(response)

# Start Bolt app
if __name__ == "__main__":
    init_db()
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
