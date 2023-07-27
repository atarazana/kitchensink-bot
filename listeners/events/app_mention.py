from logging import Logger


def app_mention_callback(client, event, logger: Logger):
    try:
        logger.info(f"app_mention_callback event: {event} client: {client}")
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
