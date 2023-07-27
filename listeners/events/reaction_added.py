from logging import Logger
import os
import re

from slack_sdk import WebClient

from db import add_vote_to_poll

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


def extract_poll_name(text: str):
    pattern = r"Poll (\w+) opened for voting.*"
    match = re.search(pattern, text)

    if match:
        return match.group(1).lstrip().rstrip()

    return


def decode_reaction(reaction: str):
    match reaction:
        case "one":
            return "option_1"
        case "two":
            return "option_2"
        case "three":
            return "option_3"
    return


def reaction_added_callback(body, event, say, logger: Logger):
    # print(f'handle_reaction_added body: {body} event: {event} client: {client}')

    user_id = event["user"]
    item = event["item"]
    reaction = event["reaction"]
    option = decode_reaction(reaction)

    try:
        # Call the conversations.history API method to fetch the reacted message
        response = client.conversations_history(channel=item["channel"], latest=item["ts"], inclusive=True, limit=1)

        messages = response["messages"]
        if messages:
            message = messages[0]
            poll_name = extract_poll_name(message["text"])
            if poll_name is None:
                return
            if option is None:
                say(f"bad reaction {reaction}, should be: one, two, or three")
                return
            logger.debug(f"User {user_id} reacted to this poll {poll_name} with {reaction}")
            add_vote_to_poll(poll_name, option)
        else:
            print("Message not found.")
    except Exception as e:
        say(f"Failed handling reaction: {e}")
