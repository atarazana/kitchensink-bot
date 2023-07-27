from slack_bolt import Ack, Respond
from logging import Logger


def help_command_callback(command, ack: Ack, respond: Respond, logger: Logger):
    try:
        ack()
        help = f"""
        Hi there <@{command['user_name']}>. I'm your friendly neighbourhood DevOps bot.
        Use _chat-bot set-app @user application namespace_ to set the current app for a user
        Use _chat-bot get-app @user_ to get the current app (or leave user out for the current user)
        Use _chat-bot logs_ to get the logs for the app that is set for the current user
        Use _chat-bot describe_ to get the description for the app that is set for the current user
        """
        # respond(f"help for '{command['text']}' _chat-bot")
        respond(help)
    except Exception as e:
        logger.error(e)
