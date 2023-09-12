import os
import re
import subprocess
from collections import Counter

from slack_bolt import Ack, Respond
from logging import Logger

from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock

from db import close_polls, get_action_by_poll_name_and_option, get_poll, close_poll, open_poll, create_poll, get_votes

POLL_OPEN_EXAMPLE_CALL = "/poll open my_poll [Delete Limit,Delete Quota,Delete all]"
POLL_CLOSE_EXAMPLE_CALL = "/poll close my_poll"
POLL_GET_EXAMPLE_CALL = "/poll get my_poll"

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


def poll_command_callback(command, ack: Ack, respond: Respond, logger: Logger):
    try:
        ack()
        logger.debug(f" command => {command}")

        verb_pattern = r"(open|close|get)\s*(.*)"
        verb_match = re.search(verb_pattern, command["text"])

        if verb_match:
            verb = verb_match.group(1)
            subject = verb_match.group(2)
            logger.debug(f" verb => {verb} subject => {subject}")

            match verb.lower():
                case "create":
                    (poll_name, option_1, option_2, option_3) = extract_args_create(subject, logger)
                    respond(f"Creating poll {poll_name}")
                    create_poll(poll_name, option_1, option_2, option_3)
                    respond(
                        f"Poll {poll_name} created but closed:\n- :two: {option_1}\n- :one: {option_2}\n- :three: {option_3}"
                    )
                case "open":
                    (poll_name) = extract_args_open(subject, logger)
                    respond(f"Reading poll {poll_name}")
                    (poll,error) = open_poll(poll_name)
                    if error:
                        respond(f"Poll {poll_name} can't be opened. {error}")
                    else:
                        respond(f"Poll {poll}")
                        post_poll_opening_message(poll, client, command["channel_name"], logger)
                case "close":
                    respond(f"Closing poll(s)")
                    polls_closed = close_polls()
                    logger.info(f"polls_closed: {polls_closed}")
                    if polls_closed is not None and len(polls_closed) == 1:
                        poll_name = polls_closed[0]['poll_name']
                        # If there are no votes... option_1 is the one selected
                        winner_option = 'option_1'
                        votes = get_votes(poll_name)
                        if len(votes) > 0: 
                            count_by_option = Counter(item["option"] for item in votes)
                            max_option, max_count = count_by_option.most_common(1)[0]
                            print(f"The most voted option is {max_option} with count={max_count}")
                            winner_option = max_option                        

                        client.chat_postMessage(
                            channel=command["channel_name"],
                            text=f"Poll *{poll_name}* closed, the winner is option *'{polls_closed[0][winner_option]}'*",
                        )
                        action = get_action_by_poll_name_and_option(poll_name, winner_option)
                        respond(f"Executing {action}")
                        # (action_is_slack, message) = is_action_slack(action['command'], logger)
                        if action["txt"] or action["image_url"]:
                            post_action_message(action, client, command["channel_name"], logger)

                        if action["command"]:
                            client.chat_postMessage(
                                channel=command["channel_name"],
                                text=f"About to run: {action['command']}",
                            )
                            (returncode, stdout, stderr) = execute_shell_command(action["command"])
                            respond(blocks=blocks_for_cmd_result(returncode, stdout, stderr))
                        else:
                            logger.info("There should be a command to execute")
                    else:
                        respond("There has to be one poll open and one only, try /poll open [poll_name]")
                case "get":
                    poll_name = extract_args_get(subject, logger)
                    respond(f"Getting poll {poll_name}")
                    poll = get_poll(poll_name)
                    if poll is not None:
                        respond(
                            f"Poll {poll['poll_name']} opened for voting:\n"
                            f"- :one: {poll['option_1']}\n"
                            f"- :two: {poll['option_2']}\n"
                            f"- :three: {poll['option_3']}"
                        )
                    else:
                        respond(f"No such a poll named {poll_name}")
                case _:
                    client.chat_postMessage(
                        channel=command["channel_name"],
                        text="Poll command not found!",
                    )
        else:
            logger.error("Poll command not found!")
            respond(f"Malformed command: /poll {command['text']}")
    except Exception as e:
        logger.error(e)
        respond(f"Error command: /poll {command['text']} failed with this error: {e}")


def extract_args_create(subject: str, logger: Logger):
    pattern = r"(\w+)\s+\[(.+),(.+),(.+)\]"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        option_1 = match.group(2).lstrip().rstrip()
        option_2 = match.group(3).lstrip().rstrip()
        option_3 = match.group(4).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name} option_1 => {option_1} option_2 => {option_2} option_3 => {option_3}")
    else:
        raise Exception(f"Arguments malformed for '/poll open' try this instead: {POLL_OPEN_EXAMPLE_CALL}")

    return (poll_name, option_1, option_2, option_3)


def extract_args_close(subject: str, logger: Logger):
    pattern = r"(\w+)"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name}")
    else:
        raise Exception(f"Arguments malformed for '/poll close' try this instead: {POLL_CLOSE_EXAMPLE_CALL}")

    return poll_name


def extract_args_open(subject: str, logger: Logger):
    pattern = r"(\w+)"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name}")
    else:
        raise Exception(f"Arguments malformed for '/poll open' try this instead: {POLL_OPEN_EXAMPLE_CALL}")

    return poll_name


def extract_args_get(subject: str, logger: Logger):
    pattern = r"(\w+)"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name}")
    else:
        raise Exception(f"Arguments malformed for '/poll get' try this instead: {POLL_GET_EXAMPLE_CALL}")

    return poll_name


def is_action_slack(action: str, logger: Logger):
    logger.debug(f"is_action_slack (action={action})")
    slack_pattern = r"slack.*(\{.*\})"
    slack_match = re.search(slack_pattern, action)

    logger.debug(f"slack_match {slack_match}")

    # If action is slack let's extract the message
    if slack_match:
        message = slack_match.group(1).lstrip().rstrip()
        logger.debug(f"message => {message}")
        return (True, message)

    return (False, None)


def post_poll_opening_message(poll, client: WebClient, channel: str, logger: Logger):
    logger.debug(f"post_poll_opening_message(poll={poll})")

    message = {
        "channel": channel,
        "text": f"Poll *{poll['poll_name']}* opened for voting",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"Poll *{poll['poll_name']}* opened for voting!!!"}},
            {"type": "divider"},
            {"type": "header", "text": {"type": "plain_text", "text": f":rocket:  {poll['title']}  :rocket:"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Responde *reaccionando* con uno de los iconos siguientes:\n"
                    f"• :one: {poll['option_1']}\n"
                    f"• :two: {poll['option_2']}\n"
                    f"• :three: {poll['option_3']}",
                },
            },
        ],
    }

    client.chat_postMessage(**message)


def post_action_message(action, client: WebClient, channel: str, logger: Logger):
    logger.debug(f"post_action_message(action={action})")

    message = {
        "channel": channel,
        "text": "Action executed",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": action["txt"],
                },
            },
            {"type": "image", "image_url": action["image_url"], "alt_text": "Your Image Alt Text"},
        ],
    }

    client.chat_postMessage(**message)


def execute_shell_command(command):
    try:
        # Execute the shell command and capture the output and errors
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=45)

        return (result.returncode, result.stdout, result.stderr)
    except subprocess.CalledProcessError as e:
        # An error occurred while executing the command
        print(f"Command execution failed with return code {e.returncode}")
        print(f"Error output: {e.output}")


def shorten_string_to_slack_max(s: str):
    max_length = 2900
    if len(s) > max_length:
        s = s[:max_length]
    return s


def blocks_for_cmd_result(returncode, stdout, stderr):
    blocks = [SectionBlock(text=f"*Result* after running latest command with *code({returncode})*:")]
    if stdout:
        blocks.append(SectionBlock(text=f"*Output:* {shorten_string_to_slack_max(stdout)}"))
    if stderr:
        blocks.append(SectionBlock(text=f"*Error:* {shorten_string_to_slack_max(stderr)}"))
    return blocks
