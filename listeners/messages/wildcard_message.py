from logging import Logger

from slack_bolt import BoltContext, Say
from slack_sdk import WebClient


def wildcard_message_callback(context: BoltContext, client: WebClient, say: Say, logger: Logger):
    try:
        message = context["matches"][0]
        say(f"wildcard_message_callback {message}")
    except Exception as e:
        logger.error(e)
